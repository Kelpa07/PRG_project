
document.addEventListener("DOMContentLoaded", function () {
  // Mobile nav toggle
  const navToggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".nav");
  if (navToggle && nav) {
    navToggle.addEventListener("click", () => {
      nav.classList.toggle("open");
      nav.style.display = nav.classList.contains("open") ? "flex" : "none";
    });
  }

  document.querySelectorAll(".menu-card").forEach(card => {
    card.addEventListener("click", (e) => {
      const title = card.querySelector("h4")?.innerText || "";
      const price = card.querySelector(".price")?.innerText || "";
      const addEvent = new CustomEvent("quickAdd", { detail: { title, price } });
      window.dispatchEvent(addEvent);
    });
  });

  function currencyToNumber(priceText) {
    if (!priceText) return 0;
    return parseFloat(priceText.replace(/[^\d.]/g, "")) || 0;
  }

  const CART_KEY = "project_cart_v1";
  function getCart() { try { return JSON.parse(localStorage.getItem(CART_KEY) || "[]"); } catch (e) { return [] } }
  function saveCart(c) { localStorage.setItem(CART_KEY, JSON.stringify(c)); renderCart() }

  function renderCart() {
    const cart = getCart();
    const summary = document.querySelector("#cart-summary");
    const list = document.querySelector("#cart-items");
    if (!summary || !list) return;
    list.innerHTML = "";
    let total = 0;
    cart.forEach((it, idx) => {
      const li = document.createElement("div");
      li.className = "cart-item";
      li.style.display = "flex";
      li.style.justifyContent = "space-between";
      li.style.padding = "8px 0";
      li.innerHTML = `<div>${escapeHTML(it.title)} x ${it.qty}</div><div>Nu.${(it.price * it.qty).toFixed(2)}</div>`;
      list.appendChild(li);
      total += it.price * it.qty;
    });
    summary.innerText = `Total: Nu.${total.toFixed(2)}`;
  }

  function escapeHTML(s) { return ("" + s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": "&#39;" }[c])) }

  // Add item by title/price
  function addToCart(title, price, qty = 1) {
    const cart = getCart();
    const pnum = currencyToNumber(price);
    const idx = cart.findIndex(i => i.title === title);
    if (idx >= 0) cart[idx].qty += qty;
    else cart.push({ title, price: pnum, qty });
    saveCart(cart);
  }

  // Attach to quickAdd
  window.addEventListener("quickAdd", (e) => {
    const { title, price } = e.detail;
    if (!title) return;
    addToCart(title, price, 1);
    // small notification
    flashMessage(`${title} added to cart`);
  });

  // Attach listeners on order page controls
  if (document.querySelector(".order-page")) {
    document.querySelectorAll(".food-row").forEach(row => {
      const btnPlus = row.querySelector(".add-btn");
      const btnMinus = row.querySelector(".sub-btn");
      const qtyInput = row.querySelector(".qty");
      const title = row.dataset.title;
      const price = row.dataset.price;
      if (btnPlus) btnPlus.addEventListener("click", () => {
        const q = parseInt(qtyInput.value || "0") + 1;
        qtyInput.value = q;
      });
      if (btnMinus) btnMinus.addEventListener("click", () => {
        const q = Math.max(0, parseInt(qtyInput.value || "0") - 1);
        qtyInput.value = q;
      });
      const addToCartBtn = row.querySelector(".to-cart-btn");
      if (addToCartBtn) addToCartBtn.addEventListener("click", () => {
        const q = Math.max(1, parseInt(qtyInput.value || "0"));
        addToCart(title, price, q);
        qtyInput.value = 0;
        flashMessage(`${q} × ${title} added to cart`);
      });
    });

    // cart action buttons
    const clearBtn = document.querySelector("#cart-clear");
    const checkoutBtn = document.querySelector("#cart-checkout");
    if (clearBtn) clearBtn.addEventListener("click", () => {
      localStorage.removeItem(CART_KEY);
      renderCart();
    });
    if (checkoutBtn) checkoutBtn.addEventListener("click", () => {
      flashMessage("Proceeding to checkout — (this is demo mode)");
    });

    renderCart();
  }

  // Simple flash message
  function flashMessage(txt) {
    let el = document.querySelector("#flash-msg");
    if (!el) {
      el = document.createElement("div");
      el.id = "flash-msg";
      el.style.position = "fixed";
      el.style.right = "18px";
      el.style.bottom = "18px";
      el.style.zIndex = 9999;
      el.style.background = "rgba(0,0,0,0.8)";
      el.style.color = "#fff";
      el.style.padding = "10px 14px";
      el.style.borderRadius = "8px";
      el.style.fontWeight = "700";
      document.body.appendChild(el);
    }
    el.innerText = txt;
    el.style.opacity = "1";
    setTimeout(() => { el.style.transition = "opacity .6s"; el.style.opacity = "0"; }, 1400);
  }

  // small enhancement: make images lazy and responsive (if present)
  document.querySelectorAll("img").forEach(img => {
    if (!img.hasAttribute("loading")) img.setAttribute("loading", "lazy");
  });

});
