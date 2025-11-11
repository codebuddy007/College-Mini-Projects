
let jobs = [];
const $ = id => document.getElementById(id);
const jobsTableBody = document.querySelector('#jobsTable tbody');
const output = $('output');

function renderJobs(){
  jobsTableBody.innerHTML = '';
  jobs.forEach((j, i) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${i+1}</td><td>${j.id}</td><td>${j.time}</td><td>${j.profit}</td><td><button data-i="${i}" class="del">Delete</button></td>`;
    jobsTableBody.appendChild(tr);
  });
  attachDeletes();
}

function attachDeletes(){
  document.querySelectorAll('.del').forEach(btn => {
    btn.onclick = e => {
      const i = Number(e.target.dataset.i);
      jobs.splice(i,1);
      renderJobs();
    };
  });
}

function addJobFromInputs(){
  const id = $('jobId').value.trim() || (`Task${jobs.length+1}`);
  const time = Number($('time').value);
  const pf = Number($('profit').value);
  if(!Number.isInteger(time) || time <= 0){ alert('Time must be a positive integer'); return; }
  if(!Number.isFinite(pf) || pf < 0){ alert('Profit must be non-negative'); return; }
  jobs.push({id, time, profit: pf});
  $('jobId').value=''; $('time').value=''; $('profit').value='';
  renderJobs();
}

function clearJobs(){
  if(!confirm('Clear all tasks?')) return;
  jobs = [];
  renderJobs();
  clearOutput();
}

function clearOutput(){
  output.innerHTML = '<p>No schedule yet. Click <strong>Run Scheduler</strong>.</p>';
}

function loadSample(){
  jobs = [
    {id:'Study DAA', time:2, profit:60},
    {id:'Workout', time:1, profit:40},
    {id:'Watch Lecture', time:3, profit:80},
    {id:'Cook Dinner', time:2, profit:50},
    {id:'Gaming', time:2, profit:30}
  ];
  renderJobs();
  clearOutput();
}

// Greedy Scheduler (by profit/time ratio)
function scheduleJobs(jobsInput, availableTime){
  const arr = jobsInput.map(j => ({...j, ratio: j.profit/j.time}));
  arr.sort((a,b) => b.ratio - a.ratio);
  let totalProfit = 0, totalTime = 0;
  const scheduled = [];

  for(const job of arr){
    if(totalTime + job.time <= availableTime){
      scheduled.push(job);
      totalProfit += job.profit;
      totalTime += job.time;
    }
  }
  return {scheduled, totalProfit, totalTime};
}

function renderSchedule(result){
  const {scheduled, totalProfit, totalTime} = result;
  const container = document.createElement('div');
  container.innerHTML = `<p><strong>Total Profit:</strong> ${totalProfit} | <strong>Total Time Used:</strong> ${totalTime}</p>`;

  const row = document.createElement('div');
  row.style.marginTop='8px';
  scheduled.forEach(s => {
    const span = document.createElement('span');
    span.className = 'job-badge';
    span.innerText = `${s.id} (${s.time}h, P:${s.profit})`;
    row.appendChild(span);
  });
  container.appendChild(row);
  output.innerHTML = '';
  output.appendChild(container);
}

$('addBtn').onclick = addJobFromInputs;
$('clearBtn').onclick = clearJobs;
$('sampleBtn').onclick = loadSample;
$('runBtn').onclick = () => {
  const avail = Number($('availableTime').value);
  if(!avail || avail <= 0){ alert('Enter total available time first'); return; }
  if(jobs.length === 0){ alert('Add at least one task'); return; }
  const res = scheduleJobs(jobs, avail);
  renderSchedule(res);
};

loadSample();
renderJobs();