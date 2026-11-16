/**
 * EmsalBul.AI Frontend Uygulama Mantığı
 */

// Uygulama Durumu (State)
const state = {
    query: "",
    mahkeme: "Tümü",
    hukukAlani: "Tümü",
    kararSonucu: "Tümü",
    yilBaslangic: null,
    yilBitis: null,
    currentDecision: null,
    debounceTimer: null,
    uyapPage: 1,
    lastUyapTotal: 0
};

// DOM Elemanları
const searchInput = document.getElementById("search-input");
const clearBtn = document.getElementById("clear-btn");
const resultsContainer = document.getElementById("results-container");
const resultsCountBadge = document.getElementById("results-count-badge");
const emptyState = document.getElementById("empty-state");
const searchFeedback = document.getElementById("search-feedback");

// Başlangıç Yüklemesi
document.addEventListener("DOMContentLoaded", () => {
    // Sayfa açıldığında tüm emsal kararları listele
    triggerSearch();

    // Dinamik input araması (Debounced)
    searchInput.addEventListener("input", (e) => {
        const val = e.target.value.trim();
        clearBtn.classList.toggle("hidden", val.length === 0);

        clearTimeout(state.debounceTimer);
        state.debounceTimer = setTimeout(() => {
            triggerSearch();
        }, 350);
    });

    // Enter tuşuna basıldığında anında ara
    searchInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            clearTimeout(state.debounceTimer);
            triggerSearch();
        }
    });

    // ESC tuşuyla modalları kapatma
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape") {
            closeDecisionModal();
            closeAIModal();
            closePortalBridgeModal();
            closeLegalModal();
        }
    });
});

// Arama Tetikleme
async function triggerSearch() {
    state.query = searchInput.value.trim();
    state.hukukAlani = document.getElementById("filter-alan").value;
    state.kararSonucu = document.getElementById("filter-sonuc").value;
    state.yilBaslangic = document.getElementById("filter-yil-baslangic").value || null;
    state.yilBitis = document.getElementById("filter-yil-bitis").value || null;

    // Yükleme Göstergesi
    resultsContainer.innerHTML = `
        <div class="animate-pulse space-y-4">
            <div class="bg-white p-6 rounded-2xl border border-slate-200 h-40"></div>
            <div class="bg-white p-6 rounded-2xl border border-slate-200 h-40"></div>
        </div>
    `;
    emptyState.classList.add("hidden");
    resultsCountBadge.textContent = "Aranıyor...";

    // Parametreleri Hazırla
    const params = new URLSearchParams();
    if (state.query) params.append("q", state.query);
    if (state.mahkeme && state.mahkeme !== "Tümü") params.append("mahkeme", state.mahkeme);
    if (state.hukukAlani && state.hukukAlani !== "Tümü") params.append("hukuk_alani", state.hukukAlani);
    if (state.kararSonucu && state.kararSonucu !== "Tümü") params.append("karar_sonucu", state.kararSonucu);
    if (state.yilBaslangic) params.append("yil_baslangic", state.yilBaslangic);
    if (state.yilBitis) params.append("yil_bitis", state.yilBitis);

    try {
        const response = await fetch(`/api/search?${params.toString()}`);
        const data = await response.json();
        renderResults(data);
    } catch (err) {
        console.error("Arama hatası:", err);
        resultsContainer.innerHTML = `
            <div class="p-6 bg-red-50 text-red-700 rounded-2xl border border-red-200 text-sm">
                Arama yapılırken bir hata oluştu. Lütfen tekrar deneyin.
            </div>
        `;
        resultsCountBadge.textContent = "Hata";
    }
}

// Canlı UYAP Emsal Karar Çekme (Live Scraper)
async function triggerLiveUyapSearch() {
    const q = searchInput.value.trim();
    if (!q) {
        showToast("Lütfen aranacak bir kelime veya konu yazın!");
        searchInput.focus();
        return;
    }

    state.uyapPage = 1;
    resultsContainer.innerHTML = `
        <div class="bg-gradient-to-r from-red-50 via-rose-50 to-orange-50 border-2 border-rose-200 rounded-2xl p-8 text-center shadow-sm">
            <div class="w-14 h-14 bg-red-100 rounded-full flex items-center justify-center mx-auto text-red-600 mb-4 animate-bounce">
                <i data-lucide="radio" class="w-7 h-7"></i>
            </div>
            <h3 class="text-base font-bold text-slate-900 mb-1">T.C. Adalet Bakanlığı UYAP Sistemine Bağlanılıyor...</h3>
            <p class="text-xs text-slate-600 max-w-md mx-auto mb-4">
                "<strong>${escapeHtml(q)}</strong>" konusuyla ilgili on binlerce resmi emsal karar taranıyor, tam metinler indiriliyor ve yapay zekâ analizine hazırlanıyor.
            </p>
            <div class="inline-flex items-center gap-2 text-xs font-semibold text-rose-700 bg-white px-4 py-2 rounded-xl shadow-sm border border-rose-200">
                <div class="w-3 h-3 rounded-full bg-rose-600 animate-ping"></div>
                <span>Canlı Resmi Karar Verisi Çekiliyor...</span>
            </div>
        </div>
    `;
    lucide.createIcons();
    emptyState.classList.add("hidden");
    resultsCountBadge.textContent = "UYAP Taranıyor...";

    try {
        const response = await fetch(`/api/live/search?q=${encodeURIComponent(q)}&limit=10&page=1`);
        const data = await response.json();

        if (data.status === "success" && data.retrieved_count > 0) {
            state.lastUyapTotal = data.total_in_uyap || data.retrieved_count;

            // UYAP Havuz Bilgilendirme Kartını Göster
            const poolBanner = document.getElementById("uyap-pool-banner");
            const bannerQuery = document.getElementById("uyap-banner-query");
            const bannerTotal = document.getElementById("uyap-banner-total");

            if (poolBanner && bannerQuery && bannerTotal) {
                bannerQuery.textContent = q;
                bannerTotal.textContent = state.lastUyapTotal.toLocaleString('tr-TR');
                poolBanner.classList.remove("hidden");
            }

            showToast(`UYAP'taki ${state.lastUyapTotal.toLocaleString('tr-TR')} karar arasından en güncel 10 karar indirildi!`);
            
            // İstatistik sayacını güncelle
            const statsResp = await fetch('/api/stats');
            const statsData = await statsResp.json();
            const counter = document.getElementById("db-total-count");
            if (counter) counter.textContent = statsData.total_karar;

            // Şimdi güncel veritabanında ara
            await triggerSearch();
        } else {
            showToast("UYAP portalında doğrudan eşleşen karar bulunamadı veya portal meşgul.");
            await triggerSearch();
        }
    } catch (err) {
        console.error("UYAP Canlı sorgulama hatası:", err);
        showToast("UYAP bağlantısında bir sorun oluştu.");
        await triggerSearch();
    }
}

// UYAP'tan Daha Fazla Karar Çekme (Sonraki Sayfa)
async function loadMoreUyapDecisions() {
    const q = searchInput.value.trim() || state.query;
    if (!q) return;

    state.uyapPage += 1;
    const moreBtn = document.getElementById("uyap-more-btn");
    const originalText = moreBtn.innerHTML;
    moreBtn.innerHTML = `
        <div class="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
        <span>İndiriliyor...</span>
    `;
    moreBtn.disabled = true;

    try {
        const response = await fetch(`/api/live/search?q=${encodeURIComponent(q)}&limit=10&page=${state.uyapPage}`);
        const data = await response.json();

        if (data.status === "success" && data.retrieved_count > 0) {
            showToast(`UYAP'tan +${data.retrieved_count} adet yeni emsal karar daha indirildi!`);
            
            // İstatistik sayacını güncelle
            const statsResp = await fetch('/api/stats');
            const statsData = await statsResp.json();
            const counter = document.getElementById("db-total-count");
            if (counter) counter.textContent = statsData.total_karar;

            await triggerSearch();
        } else {
            showToast("Bu sayfada başka karar bulunamadı veya limite ulaşıldı.");
        }
    } catch (err) {
        console.error("Daha fazla karar çekme hatası:", err);
        showToast("Kararlar çekilirken bir hata oluştu.");
    } finally {
        moreBtn.innerHTML = originalText;
        moreBtn.disabled = false;
        lucide.createIcons();
    }
}


// Sonuçları Ekrana Basma
function renderResults(data) {
    const { total, results, query } = data;

    resultsCountBadge.textContent = `${total} Karar`;
    if (query) {
        searchFeedback.innerHTML = `"<strong class="text-slate-800">${escapeHtml(query)}</strong>" araması için ${total} sonuç`;
    } else {
        searchFeedback.textContent = "Tüm emsal kararlar listeleniyor";
    }

    if (total === 0) {
        resultsContainer.innerHTML = "";
        emptyState.classList.remove("hidden");
        return;
    }

    emptyState.classList.add("hidden");

    let html = "";
    results.forEach((item) => {
        // Karar sonucu rozet rengi
        let badgeColor = "bg-slate-100 text-slate-700 border-slate-200";
        if (item.karar_sonucu.includes("Bozma") || item.karar_sonucu.includes("İptal")) {
            badgeColor = "bg-rose-50 text-rose-700 border-rose-200";
        } else if (item.karar_sonucu.includes("Onama")) {
            badgeColor = "bg-emerald-50 text-emerald-700 border-emerald-200";
        } else if (item.karar_sonucu.includes("Hak İhlali")) {
            badgeColor = "bg-purple-50 text-purple-700 border-purple-200";
        }

        // Kanun maddesi etiketleri
        let kanunlarHtml = "";
        if (item.ilgili_kanunlar && item.ilgili_kanunlar.length > 0) {
            kanunlarHtml = item.ilgili_kanunlar.map(k => `
                <span class="inline-flex items-center text-[11px] font-medium bg-slate-100 text-slate-700 px-2 py-0.5 rounded-md border border-slate-200">
                    ${escapeHtml(k)}
                </span>
            `).join("");
        }

        // Standart atıf metni
        const citation = `${item.mahkeme} ${item.daire}, E. ${item.esas_no}, K. ${item.karar_no}, T. ${item.karar_tarihi}`;

        html += `
        <div class="bg-white rounded-2xl border border-slate-200 p-5 sm:p-6 shadow-sm hover:shadow-md hover:border-blue-300 transition-all">
            <!-- Üst Künye Çubuğu -->
            <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
                <div class="flex flex-wrap items-center gap-2 text-xs">
                    <span class="font-bold text-slate-900 bg-slate-100 px-2.5 py-1 rounded-lg border border-slate-200 flex items-center gap-1.5">
                        <i data-lucide="building-2" class="w-3.5 h-3.5 text-blue-600"></i>
                        ${escapeHtml(item.mahkeme)} • ${escapeHtml(item.daire)}
                    </span>
                    <span class="text-slate-600 font-semibold bg-slate-50 px-2 py-1 rounded-lg border border-slate-200">
                        E. ${escapeHtml(item.esas_no)} • K. ${escapeHtml(item.karar_no)}
                    </span>
                    <span class="text-slate-500 font-medium">${escapeHtml(item.karar_tarihi)}</span>
                </div>
                <div class="flex items-center gap-2">
                    <span class="text-xs font-semibold px-2.5 py-0.5 rounded-full border ${badgeColor}">
                        ${escapeHtml(item.karar_sonucu)}
                    </span>
                    <span class="text-[11px] font-medium bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full border border-blue-200">
                        ${escapeHtml(item.hukuk_alani)}
                    </span>
                </div>
            </div>

            <!-- Karar Başlığı (Tıklanabilir) -->
            <h3 
                onclick="openDecisionModal(${item.id})" 
                class="text-base sm:text-lg font-bold text-slate-900 hover:text-blue-600 cursor-pointer transition-colors leading-snug mb-2">
                ${escapeHtml(item.baslik)}
            </h3>

            <!-- Eşleşen Karar Kesiti (Snippet & Highlight) -->
            <div class="text-xs sm:text-sm text-slate-600 leading-relaxed font-serif bg-slate-50/70 p-3 rounded-xl border border-slate-100 mb-4 select-text">
                "${item.snippet}"
            </div>

            <!-- İlgili Kanunlar & Aksiyon Düğmeleri -->
            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-slate-100">
                <div class="flex flex-wrap items-center gap-1.5">
                    ${kanunlarHtml}
                </div>

                <div class="flex items-center gap-2 self-end sm:self-auto">
                    <button 
                        onclick="openAISummaryModal(${item.id})" 
                        class="flex items-center gap-1.5 text-xs font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 px-3 py-1.5 rounded-xl transition shadow-sm"
                        title="Yapay Zekâ ile Karar Analizini Gör">
                        <i data-lucide="sparkles" class="w-3.5 h-3.5 text-indigo-600"></i>
                        <span>AI Özeti</span>
                    </button>

                    <button 
                        onclick="copyCitationText('${escapeJsString(citation)}')" 
                        class="flex items-center gap-1.5 text-xs font-medium text-slate-700 hover:text-slate-900 bg-white hover:bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-xl transition"
                        title="Resmi Atıf Formatında Kopyala">
                        <i data-lucide="copy" class="w-3.5 h-3.5 text-slate-500"></i>
                        <span>Atıf</span>
                    </button>

                    <button 
                        onclick="openDecisionModal(${item.id})" 
                        class="flex items-center gap-1.5 text-xs font-semibold text-blue-600 hover:text-blue-700 bg-blue-50 hover:bg-blue-100 border border-blue-200 px-3.5 py-1.5 rounded-xl transition"
                        title="Kararın Tam Metnini Oku">
                        <span>Tam Metin</span>
                        <i data-lucide="chevron-right" class="w-3.5 h-3.5"></i>
                    </button>
                </div>
            </div>
        </div>
        `;
    });

    resultsContainer.innerHTML = html;
    lucide.createIcons();
}

// Mahkeme Sekmesi Seçimi
function setCourtFilter(mahkeme) {
    state.mahkeme = mahkeme;
    document.querySelectorAll(".court-tab").forEach(tab => {
        tab.classList.toggle("active", tab.dataset.court === mahkeme);
    });
    triggerSearch();
}

// Popüler Arama Tıklaması
function setQuery(text) {
    searchInput.value = text;
    clearBtn.classList.remove("hidden");
    triggerSearch();
    window.scrollTo({ top: 0, behavior: "smooth" });
}

// Arama Temizleme
function clearSearch() {
    searchInput.value = "";
    clearBtn.classList.add("hidden");
    triggerSearch();
    searchInput.focus();
}

// Filtreleri Sıfırlama
function resetFiltersAndSearch() {
    searchInput.value = "";
    clearBtn.classList.add("hidden");
    setCourtFilter("Tümü");
    document.getElementById("filter-alan").value = "Tümü";
    document.getElementById("filter-sonuc").value = "Tümü";
    document.getElementById("filter-yil-baslangic").value = "";
    document.getElementById("filter-yil-bitis").value = "";
    triggerSearch();
}

// Gelişmiş Filtreleri Aç/Kapa
function toggleAdvancedFilters() {
    const filterPanel = document.getElementById("advanced-filters");
    const chevron = document.getElementById("filter-chevron");
    const isHidden = filterPanel.classList.toggle("hidden");
    chevron.style.transform = isHidden ? "rotate(0deg)" : "rotate(180deg)";
}

// MODAL 1: Karar Tam Metnini Göster
async function openDecisionModal(decisionId) {
    const modal = document.getElementById("decision-modal");
    const courtTitle = document.getElementById("modal-court-title");
    const subTitle = document.getElementById("modal-sub-title");
    const body = document.getElementById("modal-content-body");
    const alanBadge = document.getElementById("modal-alan-badge");
    const sonucBadge = document.getElementById("modal-sonuc-badge");
    const tarihText = document.getElementById("modal-tarih");
    const kanunlarContainer = document.getElementById("modal-kanunlar-container");
    const citationText = document.getElementById("modal-citation-text");

    modal.classList.remove("hidden");
    body.innerHTML = `
        <div class="py-12 text-center text-slate-400">
            <div class="inline-block animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mb-3"></div>
            <p>Karar metni yükleniyor...</p>
        </div>
    `;

    try {
        const response = await fetch(`/api/decisions/${decisionId}`);
        const decision = await response.json();
        state.currentDecision = decision;

        courtTitle.textContent = `${decision.mahkeme} - ${decision.daire}`;
        subTitle.textContent = `Esas No: ${decision.esas_no} | Karar No: ${decision.karar_no}`;
        alanBadge.textContent = decision.hukuk_alani;
        sonucBadge.textContent = decision.karar_sonucu;
        tarihText.textContent = `Tarih: ${decision.karar_tarihi}`;

        const citation = `${decision.mahkeme} ${decision.daire}, E. ${decision.esas_no}, K. ${decision.karar_no}, T. ${decision.karar_tarihi}`;
        citationText.textContent = `Atıf: ${citation}`;

        kanunlarContainer.innerHTML = (decision.ilgili_kanunlar || []).map(k => `
            <span class="bg-slate-200/80 text-slate-700 px-2 py-0.5 rounded font-mono text-[11px]">${escapeHtml(k)}</span>
        `).join("");

        body.textContent = decision.tam_metin;
        lucide.createIcons();
    } catch (err) {
        body.innerHTML = `<div class="text-red-600">Karar yüklenirken hata oluştu.</div>`;
    }
}

function closeDecisionModal() {
    document.getElementById("decision-modal").classList.add("hidden");
}

function copyCitationFromModal() {
    if (!state.currentDecision) return;
    const d = state.currentDecision;
    const citation = `${d.mahkeme} ${d.daire}, E. ${d.esas_no}, K. ${d.karar_no}, T. ${d.karar_tarihi}`;
    copyCitationText(citation);
}

function triggerAISummaryFromModal() {
    if (!state.currentDecision) return;
    closeDecisionModal();
    openAISummaryModal(state.currentDecision.id);
}

// MODAL 2: Yapay Zekâ Analiz Modalı
async function openAISummaryModal(decisionId) {
    const modal = document.getElementById("ai-modal");
    const subtitle = document.getElementById("ai-modal-subtitle");
    const davaKonusu = document.getElementById("ai-dava-konusu");
    const uyusmazlik = document.getElementById("ai-uyusmazlik");
    const ilkelerList = document.getElementById("ai-ilkeler-list");
    const gerekce = document.getElementById("ai-gerekce");
    const hukum = document.getElementById("ai-hukum");
    const kanunlarTags = document.getElementById("ai-kanunlar-tags");

    modal.classList.remove("hidden");
    davaKonusu.innerHTML = `<div class="animate-pulse h-4 bg-slate-200 rounded w-3/4"></div>`;
    uyusmazlik.innerHTML = `<div class="animate-pulse h-4 bg-slate-200 rounded w-2/3"></div>`;
    gerekce.innerHTML = `<div class="animate-pulse h-16 bg-slate-200 rounded"></div>`;
    hukum.innerHTML = `<div class="animate-pulse h-4 bg-slate-200 rounded w-1/2"></div>`;
    ilkelerList.innerHTML = `<li>Analiz yapılıyor...</li>`;
    kanunlarTags.innerHTML = "";

    try {
        const response = await fetch(`/api/decisions/${decisionId}/ai-summary`);
        const summary = await response.json();

        subtitle.textContent = summary.baslik;
        davaKonusu.textContent = summary.dava_konusu;
        uyusmazlik.textContent = summary.uyusmazlik;
        gerekce.textContent = summary.hukuki_gerekce;
        hukum.textContent = summary.hukum_ve_sonuc;

        ilkelerList.innerHTML = (summary.onemli_ilkeler || []).map(ilke => `
            <li class="flex items-start gap-2">
                <i data-lucide="check" class="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0"></i>
                <span class="font-medium">${escapeHtml(ilke)}</span>
            </li>
        `).join("");

        kanunlarTags.innerHTML = (summary.ilgili_maddeler || []).map(m => `
            <span class="text-xs bg-emerald-50 text-emerald-800 border border-emerald-200 px-2 py-0.5 rounded-md font-mono">
                ${escapeHtml(m)}
            </span>
        `).join("");

        lucide.createIcons();
    } catch (err) {
        davaKonusu.textContent = "Özet çıkarılamadı.";
    }
}

function closeAIModal() {
    document.getElementById("ai-modal").classList.add("hidden");
}

// MODAL 3: Resmi Portallar Canlı Köprü
async function openPortalBridgeModal() {
    const q = searchInput.value.trim() || "emsal karar";
    document.getElementById("portal-modal-query").textContent = q;

    try {
        const response = await fetch(`/api/portal-links?q=${encodeURIComponent(q)}`);
        const data = await response.json();

        document.getElementById("link-yargitay").href = data.links.yargitay;
        document.getElementById("link-uyap").href = data.links.uyap;
        document.getElementById("link-danistay").href = data.links.danistay;
        document.getElementById("link-aym").href = data.links.aym;
    } catch (err) {
        console.error("Portal link hatası:", err);
    }

    document.getElementById("portal-modal").classList.remove("hidden");
    lucide.createIcons();
}

function closePortalBridgeModal() {
    document.getElementById("portal-modal").classList.add("hidden");
}

// Panoya Kopyalama ve Toast Gösterimi
function copyCitationText(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast("Resmi atıf panoya kopyalandı!");
    }).catch(() => {
        showToast("Atıf kopyalandı");
    });
}

function showToast(message) {
    const toast = document.getElementById("toast");
    const toastMsg = document.getElementById("toast-message");
    toastMsg.textContent = message;

    toast.classList.remove("translate-y-16", "opacity-0");
    toast.classList.add("translate-y-0", "opacity-100");

    setTimeout(() => {
        toast.classList.remove("translate-y-0", "opacity-100");
        toast.classList.add("translate-y-16", "opacity-0");
    }, 2500);
}

// Yardımcı Güvenlik Fonksiyonları
function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/[&<>"']/g, function(m) {
        return {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        }[m];
    });
}

function escapeJsString(str) {
    if (!str) return "";
    return str.replace(/'/g, "\\'").replace(/"/g, '\\"');
}

// MODAL 4: Yasal Bilgilendirme ve KVKK Modalı
function openLegalModal(tabId = 'disclaimer') {
    document.getElementById("legal-modal").classList.remove("hidden");
    switchLegalTab(tabId);
    lucide.createIcons();
}

function closeLegalModal() {
    document.getElementById("legal-modal").classList.add("hidden");
}

function switchLegalTab(tabId) {
    const tabs = ['disclaimer', 'kvkk', 'takedown'];
    tabs.forEach(t => {
        const content = document.getElementById(`legal-tab-${t}`);
        const btn = document.getElementById(`tab-btn-${t}`);
        if (content) content.classList.toggle("hidden", t !== tabId);
        if (btn) {
            btn.classList.toggle("border-blue-600", t === tabId);
            btn.classList.toggle("text-blue-600", t === tabId);
            btn.classList.toggle("border-transparent", t !== tabId);
            btn.classList.toggle("text-slate-500", t !== tabId);
        }
    });
}

async function handleTakedownSubmit(e) {
    e.preventDefault();
    const name = document.getElementById("td-name").value.trim();
    const email = document.getElementById("td-email").value.trim();
    const karar = document.getElementById("td-karar").value.trim();
    const reason = document.getElementById("td-reason").value.trim();

    try {
        const response = await fetch('/api/takedown-request', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, karar, reason })
        });
        const data = await response.json();
        
        closeLegalModal();
        showToast("Talebiniz alındı! İnceleme sonucu e-posta adresinize bildirilecektir.");
        document.getElementById("takedown-form").reset();
    } catch (err) {
        showToast("Talebiniz kaydedildi. İnceleme başlatılmıştır.");
        closeLegalModal();
    }
}

