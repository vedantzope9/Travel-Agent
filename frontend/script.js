
const indianCities = [
    {city:"Delhi",state:"Delhi",code:"DEL"},{city:"Mumbai",state:"Maharashtra",code:"BOM"},
    {city:"Bengaluru",state:"Karnataka",code:"BLR"},{city:"Hyderabad",state:"Telangana",code:"HYD"},
    {city:"Chennai",state:"Tamil Nadu",code:"MAA"},{city:"Kolkata",state:"West Bengal",code:"CCU"},
    {city:"Ahmedabad",state:"Gujarat",code:"AMD"},{city:"Pune",state:"Maharashtra",code:"PNQ"},
    {city:"Goa",state:"Goa",code:"GOI"},{city:"Jaipur",state:"Rajasthan",code:"JAI"},
    {city:"Lucknow",state:"Uttar Pradesh",code:"LKO"},{city:"Kochi",state:"Kerala",code:"COK"},
    {city:"Thiruvananthapuram",state:"Kerala",code:"TRV"},{city:"Nagpur",state:"Maharashtra",code:"NAG"},
    {city:"Indore",state:"Madhya Pradesh",code:"IDR"},{city:"Varanasi",state:"Uttar Pradesh",code:"VNS"},
    {city:"Patna",state:"Bihar",code:"PAT"},{city:"Bhopal",state:"Madhya Pradesh",code:"BHO"},
    {city:"Raipur",state:"Chhattisgarh",code:"RPR"},{city:"Ranchi",state:"Jharkhand",code:"IXR"},
    {city:"Bhubaneswar",state:"Odisha",code:"BBI"},{city:"Guwahati",state:"Assam",code:"GAU"},
    {city:"Dehradun",state:"Uttarakhand",code:"DED"},{city:"Chandigarh",state:"Chandigarh",code:"IXC"},
    {city:"Amritsar",state:"Punjab",code:"ATQ"},{city:"Surat",state:"Gujarat",code:"STV"},
    {city:"Vadodara",state:"Gujarat",code:"BDQ"},{city:"Rajkot",state:"Gujarat",code:"RAJ"},
    {city:"Agra",state:"Uttar Pradesh",code:"AGR"},{city:"Udaipur",state:"Rajasthan",code:"UDR"},
    {city:"Jodhpur",state:"Rajasthan",code:"JDH"},{city:"Mangalore",state:"Karnataka",code:"IXE"},
    {city:"Madurai",state:"Tamil Nadu",code:"IXM"},{city:"Tiruchirappalli",state:"Tamil Nadu",code:"TRZ"},
    {city:"Coimbatore",state:"Tamil Nadu",code:"CJB"},{city:"Port Blair",state:"Andaman & Nicobar",code:"IXZ"},
    {city:"Shillong",state:"Meghalaya",code:"SHL"},{city:"Imphal",state:"Manipur",code:"IMF"},
    {city:"Aizawl",state:"Mizoram",code:"AJL"},{city:"Dimapur",state:"Nagaland",code:"DMU"},
    {city:"Agartala",state:"Tripura",code:"IXA"},{city:"Leh",state:"Ladakh",code:"IXL"},
    {city:"Srinagar",state:"Jammu & Kashmir",code:"SXR"},{city:"Jammu",state:"Jammu & Kashmir",code:"IXJ"},
    {city:"Kanpur",state:"Uttar Pradesh",code:"KNU"},{city:"Gaya",state:"Bihar",code:"GAY"},
    {city:"Aurangabad",state:"Maharashtra",code:"IXU"},{city:"Silchar",state:"Assam",code:"IXS"},
    {city:"Tezpur",state:"Assam",code:"TEZ"},{city:"Dibrugarh",state:"Assam",code:"DIB"},
    {city:"Jorhat",state:"Assam",code:"JRH"}
  ];
  

  const $ = s => document.querySelector(s);
  const show = el => el.classList.add('revealed');
  const hide = el => el.classList.remove('revealed');
  
  function toast(msg,err=false){
    const t = $('#toast');
    t.textContent = msg;
    t.style.display = 'block';
    t.style.borderColor = err? 'rgba(255,100,100,.16)' : 'rgba(34,211,238,.08)';
    setTimeout(()=> t.style.display='none', 2800);
  }
  

  function createSuggestionLabel(c, query){
    // bold the matched portion (simple highlight)
    const text = `${c.city}, ${c.state} (${c.code})`;
    const q = (query||'').trim().toLowerCase();
    if(!q) return text;
    const idx = c.city.toLowerCase().indexOf(q);
    if(idx !== -1){
      return `${c.city.slice(0,idx)}<span class="match">${c.city.slice(idx, idx+q.length)}</span>${c.city.slice(idx+q.length)}, ${c.state} (${c.code})`;
    }
    const idx2 = c.state.toLowerCase().indexOf(q);
    if(idx2 !== -1){
      return `${c.city}, ${c.state.slice(0,idx2)}<span class="match">${c.state.slice(idx2, idx2+q.length)}</span>${c.state.slice(idx2+q.length)} (${c.code})`;
    }
    return text;
  }
  
  function attachAutocomplete(inputEl){
    // wrap input so the suggestion box can be absolute
    const wrapper = document.createElement('div');
    wrapper.style.position = 'relative';
    inputEl.parentNode.insertBefore(wrapper, inputEl);
    wrapper.appendChild(inputEl);
  
    const list = document.createElement('div');
    list.className = 'autocomplete-list';
    list.style.display = 'none';
    wrapper.appendChild(list);
  
    let focusedIndex = -1;
    let currentMatches = [];
  
    function renderList(matches, q){
      list.innerHTML = '';
      if(!matches.length){ list.style.display='none'; return; }
      matches.forEach((c, i) => {
        const item = document.createElement('div');
        item.className = 'autocomplete-item';
        item.innerHTML = createSuggestionLabel(c, q) + `<div class="small" style="opacity:.7;margin-top:6px">${c.city} · ${c.state} · India</div>`;
        item.addEventListener('mouseenter', ()=> { focusedIndex = i; updateFocus(); });
        item.addEventListener('mouseleave', ()=> { focusedIndex = -1; updateFocus(); });
        item.addEventListener('click', ()=> {
          selectItem(c, inputEl);
        });
        list.appendChild(item);
      });
      focusedIndex = -1;
      updateFocus();
      list.style.display = 'block';
    }
  
    function updateFocus(){
      const items = list.querySelectorAll('.autocomplete-item');
      items.forEach((it, idx)=> {
        it.style.background = idx === focusedIndex ? 'rgba(255,255,255,.03)' : 'transparent';
        it.style.transform = idx === focusedIndex ? 'translateX(4px)' : 'none';
      });
    }
  
    function selectItem(c, input){
      // show readable label but store code in data-code
      input.value = `${c.city}, ${c.state} (${c.code})`;
      input.dataset.code = c.code;
      list.style.display = 'none';
      input.dispatchEvent(new Event('change'));
    }
  
    function hideList(){
      list.style.display = 'none';
      focusedIndex = -1;
    }
  
    inputEl.addEventListener('input', (e)=>{
      const q = inputEl.value.trim().toLowerCase();
      inputEl.removeAttribute('data-code'); // user changed text -> reset code unless they pick
      if(!q){ hideList(); return; }
      // match city, state, code
      const matches = indianCities.filter(c =>
        c.city.toLowerCase().includes(q) ||
        c.state.toLowerCase().includes(q) ||
        c.code.toLowerCase().includes(q)
      ).slice(0,12);
      currentMatches = matches;
      renderList(matches, q);
    });
  
    // keyboard nav
    inputEl.addEventListener('keydown', (ev)=>{
      const items = list.querySelectorAll('.autocomplete-item');
      if(list.style.display === 'block' && items.length){
        if(ev.key === 'ArrowDown'){ ev.preventDefault(); focusedIndex = (focusedIndex + 1) % items.length; updateFocus(); }
        else if(ev.key === 'ArrowUp'){ ev.preventDefault(); focusedIndex = (focusedIndex - 1 + items.length) % items.length; updateFocus(); }
        else if(ev.key === 'Enter'){ ev.preventDefault(); if(focusedIndex >=0 && currentMatches[focusedIndex]) selectItem(currentMatches[focusedIndex], inputEl); }
        else if(ev.key === 'Escape'){ hideList(); }
      }
    });
  
    // close when clicking outside
    document.addEventListener('click', (ev)=> {
      if(!wrapper.contains(ev.target)) hideList();
    });
  }
  
  // attach autocompletes on DOM inputs
  attachAutocomplete(document.getElementById('source'));
  attachAutocomplete(document.getElementById('destination'));
  
  
  const today = new Date();
  const yyyy = today.getFullYear(), mm = String(today.getMonth()+1).padStart(2,'0'), dd = String(today.getDate()).padStart(2,'0');
  document.getElementById('date').min = `${yyyy}-${mm}-${dd}`;
  

  const API_TRAVEL = 'http://127.0.0.1:8000/travel-guide';

//   async function fetchPlan({sourceCode, destinationCode, date}) {
//     try {
//       const res = await fetch(API_TRAVEL, {
//         method: 'POST',
//         headers: {'Content-Type': 'application/json'},
//         body: JSON.stringify({
//           source: sourceCode,
//           destination: destinationCode,
//           journey_date: date 
//         })
//       });
//       console.log({ sourceCode, destinationCode, date });
//       if (!res.ok) throw new Error('travel-guide endpoint not ok');
//       return await res.json();
//     } catch (e) {
//       toast('Failed to fetch from /travel-guide', true);
//       throw e;
//     }
//   }

async function fetchTravelGuide(payload) {
    const res = await fetch("http://127.0.0.1:8000/travel-guide", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    return data.result; // always JSON now
  }
  
  
  
  function normalizeFromText(d){
    const text = d.text || '';
    const images = d.images || [];
    const nearby = [];
    text.split(/\n|\./).forEach(line=>{
      const t = line.trim(); if(!t) return;
      if(/park|temple|fort|museum|garden|lake|beach|hill|palace|zoo|waterpark|waterfall/i.test(t)) nearby.push(t.replace(/^\d+\.|^-\s*/,''));
    });
    return {info:text, nearby, flights: d.flights || [], images};
  }
  
  /* ===========
     Renderers
     =========== */
  function renderHighlights(text){
    const el = $('#highlights'); el.innerHTML = '';
    if(!text){ el.textContent = 'No description available.'; return; }
    text.split(/\n\n+/).forEach(p=>{
      const para = document.createElement('p'); para.className = 'small';
      para.textContent = p.trim();
      el.appendChild(para);
    });
  }
  
  function renderNearby(list){
    const el = $('#nearby'); el.innerHTML = '';
    if(!list || !list.length){ el.innerHTML = '<span class="chip">No nearby places found</span>'; return; }
    list.slice(0,24).forEach(n=>{
      const s = document.createElement('div'); s.className = 'chip'; s.textContent = n; el.appendChild(s);
    });
  }
  
  function renderFlights(flights){
    const tb = $('#flightsBody'); tb.innerHTML = '';
    if(!flights || !flights.length){ tb.innerHTML = '<tr><td colspan="6" class="small" style="color:var(--muted)">No flights found for the selected date.</td></tr>'; return; }
    flights.forEach(f=>{
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${esc(f.airline||'')}</td><td>${esc(f.flight_no||f.flight||'')}</td>
        <td>${esc(f.depart||f.departure_time||'')}</td><td>${esc(f.arrive||f.arrival_time||'')}</td>
        <td>${esc(f.duration||'')}</td><td class="price">${esc(f.price||f.fare||'')}</td>`;
      tb.appendChild(tr);
    });
  }
  
  function renderGallery(images){
    const g = $('#gallery'); g.innerHTML = '';
    if(!images || !images.length){ g.innerHTML = '<div class="chip">No images found</div>'; return; }
    images.slice(0,40).forEach((u,i)=>{
      const tile = document.createElement('div'); tile.className = 'tile';
      const img = document.createElement('img'); img.loading='lazy'; img.src = u; img.alt = 'place'; img.onerror = ()=> tile.remove();
      const badge = document.createElement('div'); badge.className='badge'; badge.textContent = `#${i+1}`;
      tile.appendChild(img); tile.appendChild(badge); g.appendChild(tile);
    });
  }

  //Parse the Pi result

  function parseApiResult(d) {
    let res = {
      info: "",
      nearby: [],
      flights: [],
      images: []
    };
  
    try {
      let parsed;
  
      // If backend returned stringified JSON inside result
      if (typeof d === "string") {
        const cleaned = d.replace(/```json|```/g, "").trim();
        parsed = JSON.parse(cleaned);
      } else if (d.result && typeof d.result === "string") {
        const cleaned = d.result.replace(/```json|```/g, "").trim();
        parsed = JSON.parse(cleaned);
      } else if (d.result && typeof d.result === "object") {
        parsed = d.result;
      } else {
        parsed = d;
      }
  
      // ✅ Destination info
      if (parsed.destination) {
        res.info = parsed.destination.overview || parsed.destination.description || "";
      } else if (parsed["destination overview"]) {
        res.info = parsed["destination overview"];
      } else if (parsed.destination_name) {
        res.info = parsed.destination_name;
      }
  
      // ✅ Attractions / nearby
      if (Array.isArray(parsed.attractions)) {
        res.nearby = parsed.attractions.map(a => a.name || a.title || "").filter(Boolean);
        parsed.attractions.forEach(a => {
          if (a.images) res.images.push(...a.images);
        });
      }
  
      // ✅ Flights
      if (Array.isArray(parsed.flights)) {
        res.flights = parsed.flights.map(f => ({
          airline: f.airline || "",
          flight: f.flight_number || f.flight_no || "",
          depart: f.departure || f.departure_time || f.depart || "",
          arrive: f.arrival || f.arrival_time || f.arrive || "",
          duration: f.duration || "",
          price: f.price || f.fare || ""
        }));
      }
  
      // ✅ Weather (optional)
      if (parsed.weather) {
        if (typeof parsed.weather === "string") {
          res.info += "\n\nWeather: " + parsed.weather;
        } else if (parsed.weather.description) {
          res.info += `\n\nWeather: ${parsed.weather.description}, ${parsed.weather.temperature || ""}`;
        }
      }
  
      // ✅ Images
      if (Array.isArray(parsed.images)) {
        res.images.push(...parsed.images);
      }
  
    } catch (err) {
      console.error("Failed to parse API result as JSON:", err, d);
    }
  
    return res;
  }
  
  
  
  function esc(s){ return (s||'').toString().replace(/[&<>"]/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[ch])) }
  
  /* ===========
     Submit handler
     =========== */
  const form = document.getElementById('tripForm');
  form.addEventListener('submit', async (e)=>{
    e.preventDefault();
    // get stored code (from dataset) or try to parse parentheses at end
    const srcInput = $('#source'), dstInput = $('#destination'), date = $('#date').value;
    function codeFrom(input){
      if(input.dataset.code) return input.dataset.code;
      const m = input.value.match(/\(([A-Z]{2,4})\)$/i);
      if(m) return m[1].toUpperCase();
      // maybe user typed the code directly
      if(/^[A-Za-z]{2,4}$/.test(input.value.trim())) return input.value.trim().toUpperCase();
      return null;
    }
    const sourceCode = codeFrom(srcInput), destinationCode = codeFrom(dstInput);
    if(!sourceCode || !destinationCode || !date){ toast('Please select source, destination and date.', true); return; }
  
    // show loading
    $('#loading').style.display = 'flex';
    try{
        const res = await fetchTravelGuide({
            source: sourceCode,
            destination: destinationCode,
            journey_date: date
          });
      // reveal sections
      ['#highlightsSec','#nearbySec','#flightsSec','#gallerySec'].forEach(id => $(id).classList.add('revealed'));
  
      console.log(res);
    let parsed = res;
    if (res.result) {
        parsed = parseApiResult(res);
    }

    renderHighlights(parsed.info);
    renderNearby(parsed.nearby);
    renderFlights(parsed.flights);
    renderGallery(parsed.images);


      confetti({particleCount:120,startVelocity:30,spread:70,origin:{y:.15}});
      toast('Plan generated!');
      $('#highlightsSec').scrollIntoView({behavior:'smooth',block:'start'});
    }catch(err){
      console.error(err);
      toast('Failed to fetch plan — check backend and CORS.', true);
    }finally{
      $('#loading').style.display = 'none';
    }
  });