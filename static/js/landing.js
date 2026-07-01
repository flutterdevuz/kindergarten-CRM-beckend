// =====================================================
// KinderCRM — Landing Page JS (Single Step)
// =====================================================
document.addEventListener('DOMContentLoaded', () => {

  // ── DOM ──
  const form        = document.getElementById('regForm');
  const formState   = document.getElementById('formState');
  const successState= document.getElementById('successState');
  const submitBtn   = document.getElementById('submitBtn');
  const newAppBtn   = document.getElementById('newAppBtn');

  // ── VALIDATORS ──
  const rules = {
    name:     v => v.trim().length < 3 ? "Kamida 3 ta belgi kiriting" : null,
    region:   v => !v ? "Viloyatni tanlang" : null,
    district: v => !v ? "Tumanni tanlang" : null,
    phone:    v => {
      const d = v.replace(/\D/g,'');
      if (!d) return "Telefon raqamini kiriting";
      if (d.length < 9) return "To'liq telefon raqam kiriting";
      return null;
    },
  };

  function validate(fieldId) {
    const input = document.getElementById(fieldId);
    const errEl = document.getElementById(fieldId + 'Error');
    if (!input || !rules[fieldId]) return true;
    const err = rules[fieldId](input.value);
    if (err) {
      input.classList.add('err');
      if (errEl) errEl.textContent = err;
      return false;
    }
    input.classList.remove('err');
    if (errEl) errEl.textContent = '';
    return true;
  }

  function validateAll() {
    const fields = ['name','region','district','phone'];
    let ok = true;
    fields.forEach(f => { if (!validate(f)) ok = false; });
    return ok;
  }

  // Real-time clear on blur/input
  ['name','region','district','phone'].forEach(id => {
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener('blur',  () => validate(id));
    el.addEventListener('input', () => { if (el.classList.contains('err')) validate(id); });
    el.addEventListener('change',() => validate(id));
  });

  // ── DISTRICT DATA ──
  const districts = {
    'Toshkent shahri':   ['Chilonzor','Yakkasaroy','Mirzo Ulug\'bek','Uchtepa','Yunusobod','Shayxontohur','Olmazor','Bektemir','Sergeli','Mirobod','Yashnobod'],
    'Toshkent viloyati': ['Zangiota','Oʻrtachirchiq','Yuqorichirchiq','Qibray','Boka','Boʻstonliq','Chinoz','Parkent','Ohangaron','Pskent'],
    'Samarqand':         ['Samarqand','Urgut','Bulungʻur','Ishtixon','Kattaqoʻrgʻon','Pastdargʻom','Oqdaryo','Toyloq'],
    'Namangan':          ['Namangan','Kosonsoy','Toʻraqoʻrgʻon','Uychi','Chust','Pop','Mingbuloq','Norin'],
    "Farg'ona":          ['Fargʻona','Qoʻqon','Margʻilon','Beshariq','Bogʻdod','Dangʻara','Yozyovon','Rishton'],
    'Andijon':           ['Andijon','Asaka','Baliqchi','Buloqboshi','Izboskan','Jalolquduq','Shahrixon'],
    'Buxoro':            ['Buxoro','Kogon','Gijduvon','Qorovulbozor','Olot','Peshku','Romitan','Vobkent'],
    'Qashqadaryo':       ['Qarshi','Shahrisabz','Kasbi','Muborak','Nishon','Chirakchi','Kitob','Yakkabog\''],
    'Surxondaryo':       ['Termiz','Denov','Boysun','Sariosyo','Shoʻrchi','Uzun','Angor'],
    'Xorazm':            ['Urganch','Xiva','Gurlan','Pitnak','Shavot','Bogʻot','Xonqa'],
    'Navoiy':            ['Navoiy','Zarafshon','Uchquduq','Xatirchi','Karmana','Nurota','Tomdi'],
    'Jizzax':            ['Jizzax','Zomin','Doʻstlik','Arnasoy','Baxmal','Forish','Sharof Rashidov'],
    'Sirdaryo':          ['Guliston','Sirdaryo','Shirin','Boyovut','Mehnatobod','Sardoba','Xovos'],
    "Qoraqalpog'iston":  ['Nukus','Qoʻngʻirot','Moʻynoq','Xoʻjayli','Beruniy','Chimboy','Taxtakoʻpir'],
  };

  const regionSel   = document.getElementById('region');
  const districtSel = document.getElementById('district');

  regionSel?.addEventListener('change', () => {
    const chosen = regionSel.value;
    districtSel.innerHTML = '<option value="">Tumanni tanlang</option>';
    districtSel.disabled = !chosen;
    if (chosen && districts[chosen]) {
      districts[chosen].forEach(d => {
        const opt = document.createElement('option');
        opt.value = opt.textContent = d;
        districtSel.appendChild(opt);
      });
    }
    validate('region');
  });

  // ── PHONE FORMATTING ──
  const phoneInput = document.getElementById('phone');
  phoneInput?.addEventListener('input', e => {
    let v = e.target.value.replace(/\D/g,'');
    if (v.length > 9) v = v.slice(0,9);
    // format: XX XXX XX XX
    const p = v.match(/^(\d{0,2})(\d{0,3})(\d{0,2})(\d{0,2})$/);
    if (p) e.target.value = [p[1],p[2],p[3],p[4]].filter(Boolean).join(' ');
  });

  // ── FORM SUBMIT ──
  form?.addEventListener('submit', async e => {
    e.preventDefault();
    if (!validateAll()) { shakeCard(); return; }

    // Loading
    setLoading(true);

    const phone = '+998' + (phoneInput?.value.replace(/\D/g,'') || '');

    const payload = {
      name:     document.getElementById('name')?.value.trim(),
      region:   regionSel?.value,
      district: districtSel?.value,
      address:  document.getElementById('address')?.value.trim() || '',
      phone,
    };

    try {
      const csrf = getCookie('csrftoken');
      const res  = await fetch('/register-kindergarten/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrf || '',
        },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (res.ok && data.success) {
        showSuccess(phone);
        showToast('success', "Arizangiz qabul qilindi! ✅");
      } else {
        // Server validation errors
        if (data.errors) {
          Object.entries(data.errors).forEach(([field, msg]) => {
            const el = document.getElementById(field);
            const err= document.getElementById(field+'Error');
            if (el) el.classList.add('err');
            if (err) err.textContent = msg;
          });
          shakeCard();
        } else {
          throw new Error(data.message || "Xatolik yuz berdi");
        }
      }
    } catch (err) {
      showToast('error', err.message || "Internetni tekshiring va qaytadan urinib ko'ring");
    } finally {
      setLoading(false);
    }
  });

  // ── SHOW SUCCESS ──
  function showSuccess(phone) {
    formState.style.display = 'none';
    successState.classList.add('show');
    const badge = document.getElementById('submittedPhone');
    if (badge) badge.textContent = '📞 ' + phone;
  }

  // ── NEW APP BUTTON ──
  newAppBtn?.addEventListener('click', () => {
    successState.classList.remove('show');
    formState.style.display = '';
    form?.reset();
    districtSel.innerHTML = '<option value="">Avval viloyat</option>';
    districtSel.disabled = true;
    ['name','region','district','phone'].forEach(id => {
      document.getElementById(id)?.classList.remove('err');
      const err = document.getElementById(id+'Error');
      if (err) err.textContent = '';
    });
    document.querySelector('.reg-card')?.scrollIntoView({behavior:'smooth',block:'center'});
  });

  // ── LOADING STATE ──
  function setLoading(on) {
    if (!submitBtn) return;
    submitBtn.disabled = on;
    const txt = submitBtn.querySelector('.btn-text');
    const ico = submitBtn.querySelector('.btn-icon');
    if (on) {
      txt.innerHTML = '<span class="spinner"></span>';
      if (ico) ico.style.display = 'none';
    } else {
      txt.textContent = 'Ariza yuborish';
      if (ico) ico.style.display = '';
    }
  }

  // ── SHAKE ──
  function shakeCard() {
    const card = document.querySelector('.reg-card');
    if (!card) return;
    card.classList.remove('shake');
    void card.offsetWidth;
    card.classList.add('shake');
    card.addEventListener('animationend', () => card.classList.remove('shake'), {once:true});
  }

  // ── CSRF ──
  function getCookie(name) {
    const v = `; ${document.cookie}`;
    const p = v.split(`; ${name}=`);
    if (p.length === 2) return p.pop().split(';').shift();
    return null;
  }

  // ── TOAST ──
  function showToast(type, msg) {
    const c = document.getElementById('toastContainer');
    if (!c) return;
    const t = document.createElement('div');
    t.className = `toast toast-${type}`;
    t.innerHTML = `<span class="toast-icon">${type==='success'?'✅':'❌'}</span><span class="toast-msg">${msg}</span>`;
    c.appendChild(t);
    setTimeout(() => {
      t.style.opacity = '0';
      t.style.transform = 'translateX(16px)';
      setTimeout(() => t.remove(), 320);
    }, 4200);
  }

  // ── NAVBAR SCROLL ──
  const navbar = document.querySelector('.navbar');
  window.addEventListener('scroll', () => {
    navbar?.classList.toggle('scrolled', window.scrollY > 50);
  }, {passive:true});

  // ── SCROLL REVEAL ──
  const revealIO = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('revealed');
        revealIO.unobserve(e.target);
      }
    });
  }, {threshold:.12, rootMargin:'0px 0px -30px 0px'});
  document.querySelectorAll('.reveal').forEach(el => revealIO.observe(el));

  // ── COUNT UP ──
  function countUp(el, target, dur=1800) {
    const suffix = el.dataset.suffix || '';
    const start = performance.now();
    const tick = now => {
      const p = Math.min((now-start)/dur, 1);
      const ease = 1 - Math.pow(1-p, 3);
      el.textContent = Math.floor(ease*target).toLocaleString() + suffix;
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }

  const counterIO = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        const t = parseInt(e.target.dataset.target);
        if (!isNaN(t)) countUp(e.target, t);
        counterIO.unobserve(e.target);
      }
    });
  }, {threshold:.5});
  document.querySelectorAll('[data-target]').forEach(el => counterIO.observe(el));

  // ── SMOOTH ANCHOR SCROLL ──
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      e.preventDefault();
      document.querySelector(a.getAttribute('href'))?.scrollIntoView({behavior:'smooth',block:'start'});
    });
  });

});
