import re

file_path = r"c:\Users\raghu\samsel1\samsel_ers\samsel-ers-system\samsel_software-fixed (2).html"

with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

start_marker = "// ════ REPORTS ════"
end_marker = "// ════ CUSTOM CLASS MANAGEMENT ════"

start_idx = text.find(start_marker)
end_idx = text.find(end_marker)

if start_idx == -1 or end_idx == -1:
    print("Markers not found!")
    exit(1)

new_code = """// ════ REPORTS ════

function rRpts(el){
  el.innerHTML=`
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;margin-bottom:0">
    <div style="font-size:15px;font-weight:700;color:var(--navy)" id="rptTitle">📊 Reports Dashboard — ${gAY().code}</div>
    <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
      <label style="display:inline-flex;align-items:center;gap:6px;font-size:12px"><input type="checkbox" ${gShowTotalRate()?'checked':''} onchange="toggleShowTotalRate(this.checked)"> Show Total Rate</label>
      <button class="btn bsm" style="background:#10b981;color:#fff" onclick="rptExportCSV()">📊 Excel/CSV</button>
      <button class="btn bsm" style="background:#c0392b;color:#fff" onclick="rRptsPrint()">📄 PDF/Print</button>
    </div>
  </div>
  <div style="border-bottom:2px solid var(--border);margin-bottom:16px;margin-top:12px"></div>
  
  <div style="display:flex;gap:20px;align-items:flex-start">
    <!-- Sidebar -->
    <div style="width:230px;background:#fff;border-radius:10px;box-shadow:var(--sh);border:1px solid var(--border);overflow:hidden;flex-shrink:0" class="print-hide">
       <div style="padding:12px 16px;background:var(--navy2);color:#fff;font-weight:700;font-size:13px">Report Categories</div>
       <div id="rptSidebar" style="padding:8px"></div>
    </div>
    
    <!-- Main Content -->
    <div style="flex:1;min-width:0;display:flex;flex-direction:column;gap:16px">
       <div id="rptFilterWrap" class="print-hide"></div>
       <div id="rptContent" style="background:#fff;border-radius:10px;box-shadow:var(--sh);border:1px solid var(--border);padding:16px;"></div>
    </div>
  </div>`;
  
  if(!window._rptCat) window._rptCat = 'delivery';
  renderRptSidebar();
  renderActiveReport();
}

const RPT_CATEGORIES = [
  { id: 'consolidated', title: 'Consolidated Reports', icon:'📋', subs: [
      {id:'school', title:'School'},
      {id:'bookshop', title:'Book Shop'},
      {id:'above30', title:'Above 30%'},
      {id:'shopwise', title:'Shopwise'},
      {id:'stockAsOn', title:'Stock As On Date'},
      {id:'openingStock', title:'Opening Stock'}
  ]},
  { id: 'abstract', title: 'Abstract Report', icon:'📊' },
  { id: 'delivery', title: 'Delivery Report', icon:'🚚' },
  { id: 'due', title: 'Due Details', icon:'⏳' },
  { id: 'overallDue', title: 'Overall Due Details', icon:'⚠️' },
  { id: 'schoolList', title: 'School List & Label', icon:'🏤' }
];

function renderRptSidebar() {
  const sb = q('#rptSidebar');
  if(!sb) return;
  sb.innerHTML = RPT_CATEGORIES.map(cat => {
    const isCatOn = window._rptCat === cat.id;
    let html = `<div style="padding:8px 12px;font-size:13px;font-weight:600;color:${isCatOn?'var(--blue)':'var(--text2)'};cursor:pointer;border-radius:6px;background:${isCatOn?'#f0f6ff':'transparent'};margin-bottom:2px;display:flex;align-items:center;gap:8px;transition:all 0.2s" onclick="swRptCat('${cat.id}')" onmouseover="this.style.background='#f7fafc'" onmouseout="this.style.background='${isCatOn?'#f0f6ff':'transparent'}'">
        <span>${cat.icon}</span> <span>${cat.title}</span>
      </div>`;
    if(cat.subs && isCatOn) {
       html += `<div style="padding-left:26px;margin-bottom:8px;margin-top:4px;display:flex;flex-direction:column;gap:3px">
         ${cat.subs.map(sub => {
            const isSubOn = window._rptSub === sub.id;
            return `<div style="padding:5px 12px;font-size:12px;color:${isSubOn?'var(--blue)':'var(--text2)'};font-weight:${isSubOn?'700':'500'};cursor:pointer;border-left:2.5px solid ${isSubOn?'var(--blue)':'transparent'};border-radius:0 4px 4px 0;background:${isSubOn?'#f7fafc':'transparent'}" onclick="swRptSub('${sub.id}')">${sub.title}</div>`;
         }).join('')}
       </div>`;
    }
    return html;
  }).join('');
}

function swRptCat(id) {
  window._rptCat = id;
  const cat = RPT_CATEGORIES.find(c=>c.id===id);
  window._rptSub = cat.subs ? cat.subs[0].id : '';
  window._rptSearch='';window._rptFilterState='';window._rptFilterExec='';window._rptDateFrom='';window._rptDateTo='';window._rptGroupType='Executive Wise';window._rptDiscount='';
  renderRptSidebar();
  renderActiveReport();
}
function swRptSub(id) {
  window._rptSub = id;
  renderRptSidebar();
  renderActiveReport();
}

function renderActiveReport() {
  const cat = window._rptCat;
  const sub = window._rptSub;
  let title = RPT_CATEGORIES.find(c=>c.id===cat)?.title;
  if(sub) title += ' — ' + RPT_CATEGORIES.find(c=>c.id===cat).subs.find(s=>s.id===sub).title;
  q('#rptTitle').innerText = '📊 ' + title + ' — ' + gAY().code;
  
  renderReportFilters();
  
  const cc = q('#rptContent');
  if(!cc) return;
  
  if(cat === 'delivery') {
    renderDeliveryReport(cc);
  } else if (cat === 'due' || cat === 'overallDue') {
    renderDueReport(cc, cat === 'overallDue');
  } else if (cat === 'schoolList') {
    renderSchoolListReport(cc);
  } else if (cat === 'consolidated' && (sub==='openingStock' || sub==='stockAsOn')) {
    renderStockReport(cc, sub==='openingStock');
  } else if (cat === 'consolidated') {
    renderConsolReport(cc, sub);
  } else {
    cc.innerHTML = `<div style="text-align:center;padding:60px;color:var(--text3);font-size:14px;font-style:italic"><div style="font-size:32px;margin-bottom:12px">🚧</div>Report "${title}" is currently under development.</div>`;
  }
}

function renderReportFilters() {
  const fw = q('#rptFilterWrap');
  if(!fw) return;
  const cat = window._rptCat;
  const sub = window._rptSub;
  
  const stateOpts = '<option value="">All States</option>' + STS.map(s => `<option value="${s.c}" ${window._rptFilterState===s.c?'selected':''}>${s.n}</option>`).join('');
  const execOpts = '<option value="">All Executives</option>' + DB.exe.filter(e=>e.act).map(e=>`<option value="${e.id}" ${window._rptFilterExec==e.id?'selected':''}>${e.name}</option>`).join('');
  
  let html = `<div style="background:#f7fafc;border:1.5px solid var(--border);border-radius:10px;padding:12px 16px;font-size:12px"><div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;">`;
  html += `<input class="fc" style="width:160px;font-size:12px;padding:7px 10px" placeholder="Search..." value="${window._rptSearch||''}" oninput="window._rptSearch=this.value;renderActiveReport()">`;
  
  if (cat !== 'schoolList') {
    html += `<select class="fc" style="width:130px;font-size:12px;padding:7px 10px" onchange="window._rptFilterState=this.value;renderActiveReport()">${stateOpts}</select>`;
  }
  if (cat === 'consolidated' || cat === 'delivery' || cat === 'due' || cat === 'overallDue') {
     if (sub !== 'stockAsOn' && sub !== 'openingStock') {
       html += `<select class="fc" style="width:140px;font-size:12px;padding:7px 10px" onchange="window._rptFilterExec=this.value;renderActiveReport()">${execOpts}</select>`;
     }
  }
  if (cat === 'delivery' || cat === 'due' || cat === 'consolidated') {
    if (sub !== 'stockAsOn' && sub !== 'openingStock') {
       html += `<div style="display:flex;align-items:center;background:#fff;border:1.5px solid var(--border);border-radius:7px;padding:0 6px"><span style="color:var(--text2);font-size:11px;padding-right:4px">From</span><input type="date" style="border:none;outline:none;font-size:12px;padding:6px 2px" value="${window._rptDateFrom||''}" onchange="window._rptDateFrom=this.value;renderActiveReport()"></div>`;
       html += `<div style="display:flex;align-items:center;background:#fff;border:1.5px solid var(--border);border-radius:7px;padding:0 6px"><span style="color:var(--text2);font-size:11px;padding-right:4px">To</span><input type="date" style="border:none;outline:none;font-size:12px;padding:6px 2px" value="${window._rptDateTo||''}" onchange="window._rptDateTo=this.value;renderActiveReport()"></div>`;
    }
  }
  if (cat === 'consolidated' && (sub === 'school' || sub === 'bookshop' || sub === 'above30' || sub === 'shopwise')) {
     const gt = window._rptGroupType||'Executive Wise';
     html += `<select class="fc" style="width:140px;font-size:12px;padding:7px 10px;background:#eef5ff;color:var(--blue);font-weight:600;border-color:#bfdbfe" onchange="window._rptGroupType=this.value;renderActiveReport()">
        <option ${gt==='Executive Wise'?'selected':''}>Executive Wise</option>
        <option ${gt==='Date Wise'?'selected':''}>Date Wise</option>
        <option ${gt==='Month Wise'?'selected':''}>Month Wise</option>
        <option ${gt==='Discount Wise'?'selected':''}>Discount Wise</option>
     </select>`;
  }
  if (cat === 'consolidated' && sub === 'above30') {
     html += `<div style="display:flex;align-items:center;background:#fff;border:1.5px solid var(--border);border-radius:7px;padding:0 8px"><span style="color:var(--text2);font-size:11px;padding-right:4px">Disc ></span><input type="number" style="border:none;outline:none;font-size:12px;width:50px;padding:6px 0" placeholder="%" value="${window._rptDiscount||30}" onchange="window._rptDiscount=this.value;renderActiveReport()"></div>`;
  }
  html += `</div></div>`;
  fw.innerHTML = html;
}

// Check if order passes filters
function _ordPassFilter(o) {
   const c = gC(o.cid); if(!c) return false;
   if(window._rptFilterState && c.state !== window._rptFilterState) return false;
   if(window._rptFilterExec && String(o.eid) !== window._rptFilterExec) return false;
   if(window._rptDateFrom && o.dt < window._rptDateFrom) return false;
   if(window._rptDateTo && o.dt > window._rptDateTo) return false;
   if(window._rptSearch) {
     const s = window._rptSearch.toLowerCase();
     if(![o.no, c.name, c.city, sn(c.state)].some(v=>v.toLowerCase().includes(s))) return false;
   }
   return true;
}

function renderDeliveryReport(cc) {
  const ayid = gAY().id;
  const dispatchOrds = DB.orders.filter(o => o.ayid === ayid && (o.st === 'Dispatched' || o.st === 'Part Dispatched') && _ordPassFilter(o));
  if(!dispatchOrds.length) { cc.innerHTML='<div style="padding:20px;text-align:center;color:var(--text3);font-style:italic">No dispatched orders found matching filters.</div>'; return; }
  
  let html = `<table style="width:100%;font-size:12.5px" id="rptTableExport"><thead><tr style="background:#f7fafc">
    <th>Order No</th><th>Date</th><th>Customer</th><th>City</th><th>Order Qty</th><th>Dispatched</th><th>Pending</th><th>Transporter</th>
  </tr></thead><tbody>`;
  dispatchOrds.forEach(o => {
    const c = gC(o.cid);
    const oQ = o.det.reduce((s,d)=>s+d.qty,0);
    const dQ = o.det.reduce((s,d)=>s+getDispatchedQty(o.id,d.sid,d.cls),0);
    html += `<tr>
      <td style="font-family:DM Mono,monospace;font-weight:700">${o.no}</td>
      <td>${fd(o.dt)}</td>
      <td style="font-weight:600">${c.name}</td>
      <td>${c.city}</td>
      <td style="text-align:center">${oQ}</td>
      <td style="text-align:center;font-weight:700;color:#0d9488">${dQ}</td>
      <td style="text-align:center;color:#ef4444">${oQ-dQ}</td>
      <td><span class="chip cb2" style="font-size:10px">${o.transport||'N/A'}</span></td>
    </tr>`;
  });
  html += `</tbody></table>`;
  cc.innerHTML = '<div style="overflow-x:auto">'+html+'</div>';
}

function renderDueReport(cc, isOverall) {
  const ayid = gAY().id;
  const dueOrds = DB.orders.filter(o => o.ayid === ayid && (o.st === 'Pending' || o.st === 'Part Dispatched') && _ordPassFilter(o));
  if(!dueOrds.length) { cc.innerHTML='<div style="padding:20px;text-align:center;color:var(--text3);font-style:italic">No pending orders found matching filters.</div>'; return; }
  
  let html = `<table style="width:100%;font-size:12.5px" id="rptTableExport"><thead><tr style="background:#f7fafc">
    <th>Order No</th><th>Date</th><th>Customer</th><th>Type</th><th>Executive</th><th>Order Qty</th><th>Pending Qty</th>${gShowTotalRate()?'<th>Approx Value</th>':''}
  </tr></thead><tbody>`;
  
  let tPend=0, tVal=0;
  dueOrds.forEach(o => {
    const c = gC(o.cid); const e = gE(o.eid);
    const oQ = o.det.reduce((s,d)=>s+d.qty,0);
    const dQ = o.det.reduce((s,d)=>s+getDispatchedQty(o.id,d.sid,d.cls),0);
    const pQ = oQ - dQ;
    if(pQ <= 0) return;
    tPend += pQ;
    
    // approx value calculation (just total rate ratio)
    let val = ot(o.det);
    if(oQ>0) val = val * (pQ/oQ);
    tVal += val;
    
    html += `<tr>
      <td style="font-family:DM Mono,monospace;font-weight:700">${o.no}</td>
      <td>${fd(o.dt)}</td>
      <td style="font-weight:600">${c.name}</td>
      <td><span class="chip ${c.type==='School'?'cb2':'cn'}" style="font-size:10px">${c.type}</span></td>
      <td>${e?e.name:'-'}</td>
      <td style="text-align:center">${oQ}</td>
      <td style="text-align:center;font-weight:700;color:#ef4444">${pQ}</td>
      ${gShowTotalRate()?`<td style="text-align:right;font-weight:600">${fc(val)}</td>`:''}
    </tr>`;
    
    // If NOT overall, show individual books due
    if(!isOverall) {
      o.det.forEach(d => {
        const d_dq = getDispatchedQty(o.id,d.sid,d.cls);
        const d_pq = d.qty - d_dq;
        if(d_pq>0){
           html += `<tr style="background:#fff8f0;border-bottom:1px dashed var(--border)">
             <td colspan="4" style="padding-left:30px;font-size:11.5px;color:var(--text2)">↳ Class: <span class="clsb" style="font-size:10px">${d.cls}</span></td>
             <td style="font-size:11.5px;color:var(--text3)">${gS(d.sid)?.shortName||''}</td>
             <td style="text-align:center;font-size:11.5px;color:var(--text3)">${d.qty}</td>
             <td style="text-align:center;font-size:11.5px;font-weight:700;color:#ef4444">${d_pq}</td>
             ${gShowTotalRate()?'<td></td>':''}
           </tr>`;
        }
      });
    }
  });
  html += `</tbody><tfoot><tr><td colspan="6" style="text-align:right;font-weight:700">TOTAL DUE:</td><td style="text-align:center;font-weight:700;color:#ef4444">${tPend}</td>${gShowTotalRate()?`<td style="text-align:right;font-weight:700">${fc(tVal)}</td>`:''}</tr></tfoot></table>`;
  cc.innerHTML = '<div style="overflow-x:auto">'+html+'</div>';
}

function renderSchoolListReport(cc) {
  let schools = DB.cust.filter(c => c.act);
  const search=window._rptSearch?.toLowerCase()||'';
  if(search) schools=schools.filter(c=>[c.name,c.city,c.code].some(v=>v.toLowerCase().includes(search)));
  if(!schools.length) { cc.innerHTML='<div style="padding:20px;text-align:center;color:var(--text3);font-style:italic">No schools/bookshops found.</div>'; return; }
  
  let html=`<table id="rptTableExport" style="width:100%;font-size:12px"><thead><tr style="background:#f7fafc">
    <th>Code</th><th>Name</th><th>Type</th><th>City</th><th>State</th><th>Contact Person</th><th>Phone</th>
  </tr></thead><tbody>`;
  schools.forEach(c => {
    html+=`<tr>
      <td style="font-family:DM Mono,monospace;font-weight:700">${c.code}</td>
      <td style="font-weight:600">${c.name}</td>
      <td><span class="chip ${c.type==='School'?'cb2':'cn'}" style="font-size:10px">${c.type}</span></td>
      <td>${c.city}</td>
      <td>${sn(c.state)}</td>
      <td>${c.con||'-'}</td>
      <td>${c.ph||'-'}</td>
    </tr>`;
  });
  html+=`</tbody></table>`;
  cc.innerHTML = '<div style="overflow-x:auto">'+html+'</div><div style="margin-top:20px;padding:12px;background:#eefaed;border:1px solid #bbf7d0;border-radius:8px;font-size:13px;color:#166534">💡 To print mailing labels, export this list to Excel/CSV using the button above and use Microsoft Word Mail Merge.</div>';
}

function renderStockReport(cc, isOpening) {
  const stock = ayStock().filter(s => isOpening ? s.type === 'opening' : true);
  if(!stock.length) { cc.innerHTML='<div style="padding:20px;text-align:center;color:var(--text3);font-style:italic">No stock data available.</div>'; return; }
  
  // Group by series and class
  let map = {}; // 'sid_cls' -> {sid, cls, qty}
  stock.forEach(s => {
    const k = s.seriesId+'_'+s.classCode;
    if(!map[k]) map[k] = {sid:s.seriesId, cls:s.classCode, in:0, out:0, name:gS(s.seriesId)?.name||''};
    if(s.type==='opening'||s.type==='in_purchase'||s.type==='in_return') map[k].in += s.qty;
    else map[k].out += s.qty;
  });
  
  const search=window._rptSearch?.toLowerCase()||'';
  let rows = Object.values(map);
  if(search) rows = rows.filter(r=>r.name.toLowerCase().includes(search) || r.cls.toLowerCase().includes(search));
  
  let html=`<table id="rptTableExport" style="width:100%;font-size:12.5px"><thead><tr style="background:#f7fafc">
    <th>Book Series</th><th>Class Code</th>${!isOpening?'<th>Total In</th><th>Total Out</th>':''}<th>${isOpening?'Opening Stock Qty':'Stock Balance As On Date'}</th>
  </tr></thead><tbody>`;
  rows.sort((a,b)=>a.sid-b.sid || CLS.indexOf(a.cls)-CLS.indexOf(b.cls)).forEach(r => {
    html+=`<tr>
      <td style="font-weight:600">${r.name}</td>
      <td><span class="clsb">${r.cls}</span></td>
      ${!isOpening?`<td style="text-align:center;color:#10b981">${r.in}</td><td style="text-align:center;color:#ef4444">${r.out}</td>`:''}
      <td style="text-align:center;font-weight:700;color:var(--navy);font-size:14px">${r.in - (!isOpening?r.out:0)}</td>
    </tr>`;
  });
  html+=`</tbody></table>`;
  cc.innerHTML = '<div style="overflow-x:auto">'+html+'</div>';
}

function renderConsolReport(cc, sub) {
  const ayid = gAY().id;
  let ords = DB.orders.filter(o => o.ayid === ayid && _ordPassFilter(o));
  
  // Custom sub filters
  if(sub === 'school') ords = ords.filter(o => gC(o.cid)?.type === 'School');
  if(sub === 'bookshop' || sub === 'shopwise') ords = ords.filter(o => gC(o.cid)?.type === 'Bookshop');
  if(sub === 'above30') {
    const thresh = parseFloat(window._rptDiscount) || 30;
    ords = ords.filter(o => o.det.some(d => d.dp >= thresh));
  }
  
  if(!ords.length) { cc.innerHTML='<div style="padding:20px;text-align:center;color:var(--text3);font-style:italic">No records found.</div>'; return; }
  
  // Grouping
  const gt = window._rptGroupType||'Executive Wise';
  let groups = {}; // key -> array of orders
  
  ords.forEach(o => {
    let k = 'Unknown';
    if(gt==='Executive Wise') k = gE(o.eid)?.name || 'Unassigned';
    else if(gt==='Date Wise') k = fd(o.dt);
    else if(gt==='Month Wise') k = new Date(o.dt).toLocaleString('default', { month: 'long', year: 'numeric' });
    else if(gt==='Discount Wise') k = 'Var Discount'; // complex, simplify to just highest discount
    
    if(!groups[k]) groups[k]=[];
    groups[k].push(o);
  });
  
  let html = `<div id="rptTableExport">`;
  Object.keys(groups).sort().forEach(gk => {
    const list = groups[gk];
    let tOrd=0, tPend=0, tVal=0;
    let tbody = '';
    list.forEach(o => {
      const c = gC(o.cid);
      const oQ = o.det.reduce((s,d)=>s+d.qty,0);
      const dQ = o.det.reduce((s,d)=>s+getDispatchedQty(o.id,d.sid,d.cls),0);
      tOrd+=oQ; tPend+=(oQ-dQ); tVal+=ot(o.det);
      tbody += `<tr>
        <td style="font-family:DM Mono,monospace">${o.no}</td>
        <td style="font-weight:600">${c?.name||'-'}</td>
        <td style="text-align:center">${oQ}</td>
        <td style="text-align:center">${oQ-dQ}</td>
        ${gShowTotalRate()?`<td style="text-align:right">${fc(ot(o.det))}</td>`:''}
      </tr>`;
    });
    
    html += `<div style="background:#f0f6ff;color:var(--navy);font-weight:700;padding:8px 14px;border:1px solid var(--border);border-bottom:none;border-radius:8px 8px 0 0;margin-top:16px;font-size:13px">${gt.replace(' Wise',':')} ${gk} <span style="font-weight:500;color:var(--text2);font-size:11px;margin-left:10px">(${list.length} orders)</span></div>
    <table style="width:100%;font-size:12px;margin-bottom:0"><thead><tr style="background:#f7fafc">
      <th>Order No</th><th>Customer</th><th>Total Ordered Qty</th><th>Pending Qty</th>${gShowTotalRate()?'<th>Order Value</th>':''}
    </tr></thead><tbody>${tbody}</tbody>
    <tfoot><tr><td colspan="2" style="text-align:right;font-weight:700">SUBTOTAL:</td><td style="text-align:center;font-weight:700">${tOrd}</td><td style="text-align:center;font-weight:700;color:#ef4444">${tPend}</td>${gShowTotalRate()?`<td style="text-align:right;font-weight:700">${fc(tVal)}</td>`:''}</tr></tfoot>
    </table>`;
  });
  html += `</div>`;
  cc.innerHTML = '<div style="overflow-x:auto">'+html+'</div>';
}

function rptGetFlatData(){
  // Helper to extract data from current visible table for CSV
  const table = q('#rptTableExport');
  if(!table) return [];
  const rows = [];
  const ths = table.querySelectorAll('th');
  if(!ths.length) return [];
  const headers = Array.from(ths).map(th=>th.innerText.trim());
  
  table.querySelectorAll('tbody tr').forEach(tr => {
     if(tr.style.display==='none' || tr.innerText.trim()==='') return;
     const tds = tr.querySelectorAll('td');
     if(tds.length === headers.length) {
        let obj = {};
        tds.forEach((td, i) => obj[headers[i]] = td.innerText.trim());
        rows.push(obj);
     }
  });
  return rows;
}

function rRptsPrint(){
  const content = q("#rptContent");
  if(!content){toast('No report to print','er');return;}
  const printHtml = `
    <style>table{width:100%;border-collapse:collapse} th,td{border:1px solid #ccc;padding:6px;text-align:left}</style>
    <div style="font-family:Arial,sans-serif;font-size:12px;padding:20px">
      <div style="text-align:center;border-bottom:2px solid #0f2744;padding-bottom:10px;margin-bottom:16px">
        <div style="font-size:18px;font-weight:700;color:#0f2744">SAMSEL PUBLICATIONS</div>
        <div style="font-size:13px;font-weight:700;margin-top:4px">${q('#rptTitle').innerText}</div>
        <div style="font-size:11px;color:#666;margin-top:2px">Generated on ${new Date().toLocaleDateString('en-IN',{day:'2-digit',month:'long',year:'numeric'})}</div>
      </div>
      ${content.innerHTML}
    </div>`;
  openPrintWindow(printHtml, 'Report Print');
}

function rptExportCSV(){
  const rows=rptGetFlatData();if(!rows.length){toast('No tabular data to export from current view','er');return;}
  const hdr=Object.keys(rows[0]);
  const csv=[hdr.join(',')].concat(rows.map(r=>hdr.map(h=>{const v=String(r[h]||'');return v.includes(',')?'"'+v+'"':v;}).join(','))).join('\n');
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));
  a.download='Report_'+gAY().code.replace(/[^0-9a-zA-Z]/g,'_')+'.csv';a.click();toast('CSV downloaded','ok');
}

function rptShareWhatsApp(){
  const t = q('#rptTitle').innerText;
  let m='*SAMSEL PUBLICATIONS*\n*'+t+'*\n'+new Date().toLocaleDateString('en-IN')+'\n\n_Please download the Full Excel/PDF for details._';
  window.open('https://wa.me/?text='+encodeURIComponent(m),'_blank');
}
function rptShareEmail(){
  const t = q('#rptTitle').innerText;
  let body='SAMSEL PUBLICATIONS\n'+t+'\n'+new Date().toLocaleDateString('en-IN')+'\n\nPlease find the details in the attached print/PDF export.';
  window.open('mailto:?subject='+encodeURIComponent(t + ' | SAMSEL')+'&body='+encodeURIComponent(body));
}

// ════ CUSTOM CLASS MANAGEMENT ════"""

text = text[:start_idx] + new_code + text[end_idx + len(end_marker):]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(text)

print(f"Replaced {len(new_code)} bytes")
