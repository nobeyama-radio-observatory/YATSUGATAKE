/* SPDX-License-Identifier: BSD-3-Clause
 * proj029 1: 2G の SPEC の記録（s45acq.Acq._spec_record_full）の中身と CRC を 1 回のなめで作る。
 * 正解は Python の道: raw = spec[::-1]（u64）、f32 = P.f32_round(raw)（u64 → double → float の最近接）、crc = P.crc32(hd, data)（zlib.crc32、IEEE）。
 * 呼ぶのは s45fast.py（ctypes）。aarch64 では ARMv8 の CRC32 命令（__crc32d。CRC32C 系ではない）、それ以外（この PC の試験）は表で。
 * 戻り値: 0 = よし、1 = 2^53 以上の値がある（Python 側で f32_round と同じ ValueError にする。そのときの out・crc は使わない）
 */
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#if defined(__aarch64__) && defined(__ARM_FEATURE_CRC32)
#include <arm_acle.h>
#define HW_CRC 1
#else
#define HW_CRC 0
#endif

/* 陽性対照（s45fast.py の posctl）。正の道はどれも 0 */
#define PC_TRUNC 1   /* 0 への切り捨て（s45acq の f32_trunc と同じ形） */
#define PC_NOREV 2   /* 逆順にしない */

#if !HW_CRC
static uint32_t crc_tab[256];
static int crc_tab_ok;
static void crc_init(void)
{
    for (uint32_t i = 0; i < 256; i++) {
        uint32_t c = i;
        for (int k = 0; k < 8; k++)
            c = c & 1 ? 0xEDB88320u ^ (c >> 1) : c >> 1;
        crc_tab[i] = c;
    }
    crc_tab_ok = 1;
}
#endif

static inline uint32_t crc_u8(uint32_t c, uint8_t b)
{
#if HW_CRC
    return __crc32b(c, b);
#else
    return crc_tab[(c ^ b) & 0xFF] ^ (c >> 8);
#endif
}

static inline uint32_t crc_u64(uint32_t c, uint64_t v)    /* v の 8 バイトをリトルエンディアンの順に */
{
#if HW_CRC
    return __crc32d(c, v);
#else
    for (int k = 0; k < 8; k++)
        c = crc_u8(c, (uint8_t)(v >> (8 * k)));
    return c;
#endif
}

/* 反転済み（zlib の内側の形）の c に buf を足す */
static uint32_t crc_buf(uint32_t c, const uint8_t *p, size_t n)
{
    while (n && ((uintptr_t)p & 7)) {
        c = crc_u8(c, *p++);
        n--;
    }
    for (; n >= 8; n -= 8, p += 8) {
        uint64_t v;
        memcpy(&v, p, 8);
        c = crc_u64(c, v);
    }
    while (n--)
        c = crc_u8(c, *p++);
    return c;
}

/* zlib.crc32(buf, init) と同じ */
uint32_t s45_crc32(uint32_t init, const uint8_t *buf, size_t n)
{
#if !HW_CRC
    if (!crc_tab_ok)
        crc_init();
#endif
    return ~crc_buf(~init, buf, n);
}

int s45_hw_crc(void)
{
    return HW_CRC;
}

void s45_nop(void)
{
}

static inline float f32_of(uint64_t u, int trunc)
{
    double d = (double)u;          /* u < 2^53 なら厳密 */
    float f = (float)d;            /* 最近接・偶数（丸めはここ 1 回） */
    if (trunc && (double)f > d)
        f = nextafterf(f, 0.0f);
    return f;
}

/* in: FFT の ch の順の u64 × n。out: f32 × n（IF の昇順 = in の逆順）。*crc = zlib.crc32(hd ＋ out) */
int s45_spec_f32(const uint64_t *in, size_t n, const uint8_t *hd, size_t hlen, float *out, uint32_t *crc, int posctl)
{
#if !HW_CRC
    if (!crc_tab_ok)
        crc_init();
#endif
    int trunc = posctl & PC_TRUNC, norev = posctl & PC_NOREV;
    uint32_t c = crc_buf(~0u, hd, hlen);
    uint64_t hi = 0;
    size_t i = 0;
    if (!trunc && !norev && !(hlen & 7)) {
        /* 正の道: 2 個ずつ（8 バイト）で CRC。hlen が 8 の倍数なので CRC の並びは out の先頭から 8 バイトずつ */
        const uint64_t *src = in + n;
        for (; i + 2 <= n; i += 2) {
            uint64_t a = src[-1 - (ptrdiff_t)i], b = src[-2 - (ptrdiff_t)i];
            hi |= a | b;
            float fa = (float)(double)a, fb = (float)(double)b;
            uint32_t wa, wb;
            memcpy(&wa, &fa, 4);
            memcpy(&wb, &fb, 4);
            out[i] = fa;
            out[i + 1] = fb;
            c = crc_u64(c, (uint64_t)wa | (uint64_t)wb << 32);
        }
    }
    for (; i < n; i++) {
        uint64_t a = norev ? in[i] : in[n - 1 - i];
        hi |= a;
        float f = f32_of(a, trunc);
        out[i] = f;
        uint32_t w;
        memcpy(&w, &f, 4);
        for (int k = 0; k < 4; k++)
            c = crc_u8(c, (uint8_t)(w >> (8 * k)));
    }
    *crc = ~c;
    return (hi >> 53) ? 1 : 0;
}

/* fmt u64（both の u64 の側）: out = in の逆順、*crc = zlib.crc32(hd ＋ out)。2^53 の検査はしない（Python の u64 の道もしない） */
int s45_spec_u64(const uint64_t *in, size_t n, const uint8_t *hd, size_t hlen, uint64_t *out, uint32_t *crc, int posctl)
{
#if !HW_CRC
    if (!crc_tab_ok)
        crc_init();
#endif
    int norev = posctl & PC_NOREV;
    uint32_t c = crc_buf(~0u, hd, hlen);
    for (size_t i = 0; i < n; i++) {
        uint64_t a = norev ? in[i] : in[n - 1 - i];
        out[i] = a;
        if (hlen & 7) {
            for (int k = 0; k < 8; k++)
                c = crc_u8(c, (uint8_t)(a >> (8 * k)));
        } else {
            c = crc_u64(c, a);
        }
    }
    *crc = ~c;
    return 0;
}

/* proj029 2: PL のリングの上の SPEC のレコード（頭 64 バイト ＋ 中身 pb バイト = u64 × n、FFT の ch の順）から、写さずに記録を作る。
 * なめ 1: 前から 1 回。PL の CRC（zlib.crc32(頭 ＋ 中身)、plring.Ring.read と同じ範囲）を取りながら、out の逆順の位置に書く（fmt 1 = f32、0 = u64）。
 * なめ 2: out（書いたばかり）に頭 hd を付けた CRC（= P.crc32(hd, data)）。
 * 戻り値: 0 = よし、1 = 2^53 以上の値がある（f32 のときだけ見る）。*crc_pl と尾の CRC の照合は呼び手が行う */
int s45_ring_spec(const uint8_t *rec, size_t n, const uint8_t *hd, size_t hlen, void *out, int fmt, uint32_t *crc, uint32_t *crc_pl, int posctl)
{
#if !HW_CRC
    if (!crc_tab_ok)
        crc_init();
#endif
    int trunc = posctl & PC_TRUNC;
    uint32_t cp = crc_buf(~0u, rec, 64);
    const uint64_t *in = (const uint64_t *)(rec + 64);
    uint64_t hi = 0;
    if (fmt == 1) {
        float *o = (float *)out;
        if (!trunc) {
            for (size_t i = 0; i < n; i++) {
                uint64_t a = in[i];
                cp = crc_u64(cp, a);
                hi |= a;
                o[n - 1 - i] = (float)(double)a;
            }
        } else {
            for (size_t i = 0; i < n; i++) {
                uint64_t a = in[i];
                cp = crc_u64(cp, a);
                hi |= a;
                o[n - 1 - i] = f32_of(a, 1);
            }
        }
        *crc = ~crc_buf(crc_buf(~0u, hd, hlen), (const uint8_t *)out, n * 4);
    } else {
        uint64_t *o = (uint64_t *)out;
        for (size_t i = 0; i < n; i++) {
            uint64_t a = in[i];
            cp = crc_u64(cp, a);
            o[n - 1 - i] = a;
        }
        *crc = ~crc_buf(crc_buf(~0u, hd, hlen), (const uint8_t *)out, n * 8);
    }
    *crc_pl = ~cp;
    return (fmt == 1 && (hi >> 53)) ? 1 : 0;
}

/* proj036: 束ね（n_sum ≧ 2）の 1 本を、PL のリングの上の SPEC のレコード（頭 64 バイト ＋ u64 × n）から写さずに器 acc へ。
 * 1 回のなめで PL の CRC（zlib.crc32(頭 ＋ 中身)、plring.Ring.read と同じ範囲）を取りながら、first なら acc = 中身、でなければ acc += 中身（u64 の和、桁あふれは
 * numpy の += と同じく 2^64 で巻く）。並びは FFT の ch の順のまま（逆順と丸めは記録のとき s45_spec_f32 / s45_spec_u64 で）。
 * posctl 1 は陽性対照（足さずに写す = 束の最後の 1 本だけが残る）。*crc_pl と尾の CRC の照合は呼び手が行う */
#define PC_NOACC 1
void s45_ring_acc(const uint8_t *rec, size_t n, uint64_t *acc, int first, uint32_t *crc_pl, int posctl)
{
#if !HW_CRC
    if (!crc_tab_ok)
        crc_init();
#endif
    uint32_t cp = crc_buf(~0u, rec, 64);
    const uint64_t *in = (const uint64_t *)(rec + 64);
    if (first || (posctl & PC_NOACC)) {
        for (size_t i = 0; i < n; i++) {
            uint64_t a = in[i];
            cp = crc_u64(cp, a);
            acc[i] = a;
        }
    } else {
        for (size_t i = 0; i < n; i++) {
            uint64_t a = in[i];
            cp = crc_u64(cp, a);
            acc[i] += a;
        }
    }
    *crc_pl = ~cp;
}

/* SpW8 M5b（ADR 0029、proj032 P-13 の spwfast.c の spw_rec_acc と同じ形）: SpW のリングの SPEC のレコード（頭 64 バイト ＋ f32 × n、type 5・fmt 1）を
 * 写さずに、PL の CRC（zlib.crc32(頭 ＋ 中身)）を取り、中身を double の器 acc に足す（first なら acc = 中身）。並びは FFT の ch の順のまま。
 * 戻り値: 中身の負か有限でない値（符号 bit か指数が全部 1）の数（0 = よし）。posctl 1 は陽性対照（足さずに写す）。
 * なめを CRC と足し込みに分ける（混ぜると命令の鎖の遅れが重なる）。足し込みは O3 でベクトル化される形（ボードの A53 で -O2 は 1 本 86 µs、O3 で 45 µs） */
__attribute__((optimize("O3")))
int s45_spw_acc(const uint8_t *rec, size_t n, double *acc, int first, uint32_t *crc_pl, int posctl)
{
#if !HW_CRC
    if (!crc_tab_ok)
        crc_init();
#endif
    uint32_t cp = crc_buf(~0u, rec, 64);
    const uint64_t *in = (const uint64_t *)(rec + 64);
    for (size_t i = 0; i < n / 2; i++)
        cp = crc_u64(cp, in[i]);
    const uint32_t *u = (const uint32_t *)(rec + 64);
    const float *f = (const float *)(rec + 64);
    int bad = 0;
    if (first || (posctl & PC_NOACC))
        for (size_t i = 0; i < n; i++)
            acc[i] = f[i];
    else
        for (size_t i = 0; i < n; i++)
            acc[i] += f[i];
    for (size_t i = 0; i < n; i++)
        bad += (u[i] >> 31) | ((u[i] & 0x7F800000u) == 0x7F800000u);
    *crc_pl = ~cp;
    return bad;
}

/* SpW8 M5b: 束ねの double の器 acc（FFT の ch の順 × n）から記録の中身を作る。out[i] = (float)acc[(n/2 − 1 − i) mod n]（IF の昇順 = s45proto.IF_ORDER）。
 * 丸めは double → float の 1 回（最近接・偶数、ADR 0029）。*crc = zlib.crc32(hd ＋ out)。numpy の acc[IF_ORDER].astype(float32) と bit で同じ */
__attribute__((optimize("O3")))
void s45_spw_rec(const double *acc, size_t n, const uint8_t *hd, size_t hlen, float *out, uint32_t *crc)
{
#if !HW_CRC
    if (!crc_tab_ok)
        crc_init();
#endif
    size_t h = n / 2;
    for (size_t i = 0; i < h; i++)            /* i < n/2: ch n/2 − 1 − i（逆順）*/
        out[i] = (float)acc[h - 1 - i];
    for (size_t i = h; i < n; i++)            /* i ≧ n/2: ch n − 1 − (i − n/2) */
        out[i] = (float)acc[n + h - 1 - i];
    uint32_t c = crc_buf(~0u, hd, hlen);
    *crc = ~crc_buf(c, (const uint8_t *)out, n * 4);
}

/* ---- SpW8 M5b: リングの [R, W) を C で 1 回なめる（s45acq.SpwBackend の C の道。Python の Bundler（f32）・_SpwRoute.poll_win と同じ規則）----
 * レコードごとに: magic・尾・PL の CRC、(core, s) → 論理の窓 j（smap）、頭の語 4 の照らし、コアごとの SEQ の飛び、DUMP_K の飛び（読み落とし）、
 * 束ねの区切り（m = round(DUMP_T / BASE)・r の一定・束 jb = m / n_sum）と double の器への足し込み。
 * 束ができた・捨てた（ev に最大 2 つ）か、type 5 でないレコード（TP など。Python が 1 本読む）か、W に着いたら戻る。
 * 戻り値: 0 W に着いた・1 ev あり・2 type 5 でないレコードの頭で止まった（*r_out がその位置）・−1 magic が違う・−2 PAD の長さが違う */
#define SPW_MAGIC_R 0x52353453u
#define SPW_MAGIC_E 0x45353453u
enum { SW_KETSU = 1, SW_R = 2, SW_JUN = 3, SW_CFG = 4, SW_N = 5, SW_CRC = 6, SW_VAL = 7, SW_ATAMA = 8 };
typedef struct {                 /* s45fast.SPW_WIN と同じ並び（全部 8 バイト） */
    int64_t n_sum, pl_nacc;
    uint64_t w4;                 /* 頭の語 4 の期待（log2N・NS・SHIFT・fmt・src。G と DUMP_H は見ない: & 0xFFFF00FFFFFF） */
    int64_t dk;                  /* 最後の DUMP_K（−1 = まだ） */
    int64_t r0, has_r0, dead, jb0, has_jb0;
    int64_t cur, jb, cnt, m_first, m_last, bad;
    int64_t cfg, sat, flags, h, n, t0, seq0;
    uint64_t acc;                /* double × nf の器の番地 */
    int64_t nf;                  /* 器の長さ（f32 の数） */
    int64_t miss, crc_bad, val_bad, pl_dumps, r_bad, drop;
} spw_win_t;
typedef struct {                 /* s45fast.SPW_EV と同じ並び。kind 1 = 束ができた・2 = 捨てた */
    int64_t kind, j, why, jb, have, k, t, n, sat, flags, h, cfg, seq;
} spw_ev_t;

static void sw_drop(spw_win_t *W, int64_t j, spw_ev_t *ev, int64_t *nev, int64_t why, int64_t jb, int64_t have)
{
    spw_ev_t *e = &ev[(*nev)++];
    memset(e, 0, sizeof *e);
    e->kind = 2; e->j = j; e->why = why; e->jb = jb; e->have = have;
    W->drop++;
}

__attribute__((optimize("O3")))
int s45_spw_scan(const uint8_t *ring, uint64_t size, uint32_t r, uint32_t w, const int8_t *smap, spw_win_t *wv, int64_t *cseq,
                 int64_t *ctr, spw_ev_t *ev, int64_t *nev, uint32_t *r_out, int64_t base, int posctl)
{
#if !HW_CRC
    if (!crc_tab_ok)
        crc_init();
#endif
    /* ctr: [0] コアごとの SEQ の飛び・[1] 動いていない流れ・[2] 頭の不一致・[3] 尾か CRC の誤り（ring_crc） */
    *nev = 0;
    while (r != w) {
        uint64_t p = r & (size - 1);
        const uint64_t *hp = (const uint64_t *)(ring + p);
        uint64_t h0 = hp[0], h7 = hp[7];
        if ((uint32_t)h0 != SPW_MAGIC_R) {
            *r_out = r;
            return -1;
        }
        unsigned ty = (h0 >> 40) & 0xFF;
        if (ty == 0) {                                     /* PAD */
            uint64_t n = h7 & 0xFFFFFFFFu;
            if (p + n != size) {
                *r_out = r;
                return -2;
            }
            r += (uint32_t)n;
            continue;
        }
        if (ty != 5) {
            *r_out = r;
            return 2;
        }
        uint64_t pb = h7 & 0xFFFFFFFFu, nb = 64 + pb;
        const uint64_t *tp = (const uint64_t *)(ring + p + nb);
        uint64_t t0w = tp[0], t1w = tp[1];
        uint64_t h1 = hp[1];
        uint32_t seq = (uint32_t)h1;
        r += (uint32_t)(nb + 64);
        if ((uint32_t)t0w != SPW_MAGIC_E || (uint32_t)(t0w >> 32) != seq) {
            ctr[3]++;
            continue;
        }
        unsigned core = (h0 >> 48) & 0xFF, s = (h0 >> 56) & 0xFF;
        if (core < 4) {
            if (cseq[core] >= 0 && seq != (uint32_t)(cseq[core] + 1))
                ctr[0]++;
            cseq[core] = seq;
        }
        int j = core < 4 ? smap[core * 256 + s] : -1;
        if (j < 0) {
            ctr[1]++;
            continue;
        }
        spw_win_t *W = &wv[j];
        if ((hp[4] & 0xFFFF00FFFFFFull) != W->w4 || (int64_t)(pb / 4) != W->nf) {
            ctr[2]++;
            continue;
        }
        int64_t k = (int64_t)(h1 >> 32);
        if (W->dk >= 0 && k <= W->dk)
            continue;                                      /* 前の RUN の残り */
        if (W->dk >= 0)
            W->miss += k - W->dk - 1;
        W->dk = k;
        W->pl_dumps++;
        if (W->dead)
            continue;
        int64_t t = (int64_t)hp[3];
        int64_t mi = (t + base / 2) / base, rr = t - mi * base;
        if (!W->has_r0) {
            W->r0 = rr; W->has_r0 = 1;
        } else if (rr - W->r0 > 1 || W->r0 - rr > 1) {
            W->r_bad++; W->dead = 1;
            if (W->cur) {
                W->cur = 0;
                sw_drop(W, j, ev, nev, SW_R, W->jb, W->cnt);
            } else
                sw_drop(W, j, ev, nev, SW_R, mi / W->n_sum, 0);
            *r_out = r;
            return 1;
        }
        int64_t jb = mi / W->n_sum;
        if (!W->has_jb0) {
            W->jb0 = jb; W->has_jb0 = 1;
        }
        if (W->cur && W->jb != jb) {
            W->cur = 0;
            sw_drop(W, j, ev, nev, SW_KETSU, W->jb, W->cnt);
        }
        /* 足し込み（s45_spw_acc と同じ）と PL の CRC */
        int first = !W->cur;
        uint32_t cp = crc_buf(~0u, ring + p, 64);
        const uint64_t *in = (const uint64_t *)(ring + p + 64);
        size_t nf = (size_t)W->nf;
        for (size_t i = 0; i < nf / 2; i++)
            cp = crc_u64(cp, in[i]);
        const uint32_t *u = (const uint32_t *)(ring + p + 64);
        const float *f = (const float *)(ring + p + 64);
        double *acc = (double *)(uintptr_t)W->acc;
        if (first || (posctl & PC_NOACC))
            for (size_t i = 0; i < nf; i++)
                acc[i] = f[i];
        else
            for (size_t i = 0; i < nf; i++)
                acc[i] += f[i];
        int nbad = 0;
        for (size_t i = 0; i < nf; i++)
            nbad += (u[i] >> 31) | ((u[i] & 0x7F800000u) == 0x7F800000u);
        int crc_bad = ~cp != (uint32_t)t1w;
        if (crc_bad) {
            W->crc_bad++; W->miss++; ctr[3]++;             /* s45acq の Python の道と同じ数え方（読み落とし ＋1・ring_crc ＋1） */
        }
        if (nbad)
            W->val_bad++;
        uint64_t h4 = hp[4], h5 = hp[5], h6 = hp[6];
        int64_t why = crc_bad ? SW_CRC : nbad ? SW_VAL : ((int64_t)(h5 & 0xFFFFFFFFu) != W->pl_nacc) ? SW_N : 0;
        if (first) {
            W->cur = 1; W->jb = jb; W->cnt = 1; W->m_first = W->m_last = mi; W->bad = why;
            W->cfg = (int64_t)(h6 & 0xFFFFFFFFu); W->sat = (int64_t)(h5 >> 32); W->flags = (int64_t)(h6 >> 32);
            W->h = (int64_t)(h4 >> 48); W->n = (int64_t)(h5 & 0xFFFFFFFFu); W->t0 = t; W->seq0 = seq;
        } else {
            if (!W->bad && mi != W->m_last + 1)
                W->bad = SW_JUN;
            if (!W->bad && (int64_t)(h6 & 0xFFFFFFFFu) != W->cfg)
                W->bad = SW_CFG;
            if (!W->bad)
                W->bad = why;
            W->m_last = mi; W->cnt++;
            W->sat += (int64_t)(h5 >> 32); W->flags |= (int64_t)(h6 >> 32); W->h |= (int64_t)(h4 >> 48); W->n += (int64_t)(h5 & 0xFFFFFFFFu);
        }
        if (W->cnt >= W->n_sum) {
            W->cur = 0;
            if (W->bad || W->m_first != jb * W->n_sum)
                sw_drop(W, j, ev, nev, W->bad ? W->bad : SW_ATAMA, jb, W->cnt);
            else {
                spw_ev_t *e = &ev[(*nev)++];
                e->kind = 1; e->j = j; e->why = 0; e->jb = jb; e->have = W->cnt; e->k = jb - W->jb0; e->t = W->t0;
                e->n = W->n; e->sat = W->sat; e->flags = W->flags; e->h = W->h; e->cfg = W->cfg; e->seq = W->seq0;
            }
        }
        if (*nev) {
            *r_out = r;
            return 1;
        }
    }
    *r_out = r;
    return 0;
}
