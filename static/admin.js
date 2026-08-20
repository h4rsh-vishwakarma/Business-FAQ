async function loadLeads() {
  const tableBody = document.getElementById("leads-table-body");
  tableBody.innerHTML = '<tr><td colspan="4">Loading leads...</td></tr>';

  try {
    const response = await fetch("/api/leads", { credentials: "include" });
    if (!response.ok) {
      throw new Error("Unable to load leads.");
    }
    const leads = await response.json();
    if (!leads.length) {
      tableBody.innerHTML = '<tr><td colspan="4">No leads captured yet.</td></tr>';
      return;
    }

    tableBody.innerHTML = leads.map((lead) => `
      <tr>
        <td>${lead.name}</td>
        <td>${lead.contact}</td>
        <td>${lead.lead_type}</td>
        <td>${new Date(lead.created_at).toLocaleString()}</td>
      </tr>
    `).join("");
  } catch (error) {
    tableBody.innerHTML = '<tr><td colspan="4">Failed to load leads.</td></tr>';
  }
}

document.getElementById("refresh-btn").addEventListener("click", loadLeads);
loadLeads();
