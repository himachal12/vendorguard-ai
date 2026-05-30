import React, { useState, useEffect, useCallback } from 'react';
import { Upload } from 'lucide-react';
import axios from 'axios';
import {
  LineChart, Line, ResponsiveContainer
} from 'recharts';
import {
  Shield, Plus, Bell, RefreshCw,
  AlertTriangle, CheckCircle, XCircle,
  Trash2, X, Download,
  ArrowUpDown
} from 'lucide-react';
import './App.css';

const API = 'https://vendorguard-backend.onrender.com';

function getRiskClass(score) {
  if (score === null || score === undefined) return 'none';
  if (score >= 61) return 'red';
  if (score >= 31) return 'yellow';
  return 'green';
}

function getRiskIcon(level) {
  if (level === 'RED' || level === 'red')
    return <XCircle size={14} />;
  if (level === 'YELLOW' || level === 'yellow')
    return <AlertTriangle size={14} />;
  return <CheckCircle size={14} />;
}

// ── Risk Report Modal ─────────────────────────────────────────
function RiskModal({ data, onClose, vendorId }) {
  if (!data) return null;
  const cls = getRiskClass(data.risk_score);
  const scoreColor = cls === 'red' ? '#f87171'
    : cls === 'yellow' ? '#fbbf24' : '#34d399';

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <h2>
          <span>🛡 {data.vendor_name} — Risk Report</span>
          <button className="modal-close" onClick={onClose}>
            <X size={18} />
          </button>
        </h2>

        {/* Score Circle */}
        <div style={{
          textAlign: 'center', marginBottom: 24,
          background: '#0f1117', borderRadius: 12, padding: 20
        }}>
          <div style={{
            fontSize: 72, fontWeight: 800,
            color: scoreColor, lineHeight: 1
          }}>
            {data.risk_score}
          </div>
          <div style={{ fontSize: 13, color: '#94a3b8', marginTop: 4 }}>
            Risk Score out of 100
          </div>
          <div className={`risk-badge ${cls}`}
            style={{ margin: '10px auto', width: 'fit-content' }}>
            {getRiskIcon(cls)} {cls.toUpperCase()} RISK
          </div>
          {data.score_change !== undefined && data.score_change !== 0 && (
            <div className={`score-change ${data.score_change > 0 ? 'up' : 'down'}`}>
              {data.score_change > 0 ? '▲' : '▼'} {Math.abs(data.score_change)} from last scan
            </div>
          )}
          <div style={{ fontSize: 12, color: '#4a5568', marginTop: 8 }}>
            {data.signals_found} signals collected •
            Confidence: {data.confidence_level}
          </div>
        </div>

        {/* Summary */}
        <div className="modal-section">
          <h3>Executive Summary</h3>
          <div className="finding-item">{data.summary}</div>
        </div>

        {/* Key Findings */}
        <div className="modal-section">
          <h3>Key Findings ({data.key_findings?.length || 0})</h3>
          {data.key_findings?.map((f, i) => (
            <div key={i} className="finding-item">• {f}</div>
          ))}
        </div>

        {/* Risk Breakdown */}
        <div className="modal-section">
          <h3>Risk Breakdown by Category</h3>
          <div className="category-grid">
            {Object.entries(data.risk_categories || {}).map(([k, v]) => {
              const c = getRiskClass(v);
              return (
                <div key={k} className="category-item">
                  <div className="cat-label">
                    {k.replace('_risk', '').replace('_', ' ')}
                  </div>
                  <div className="cat-score" style={{
                    color: c === 'red' ? '#f87171'
                      : c === 'yellow' ? '#fbbf24' : '#34d399'
                  }}>
                    {v}/100
                  </div>
                  {/* Mini bar */}
                  <div className="score-bar" style={{ marginTop: 6 }}>
                    <div className={`score-bar-fill ${c}`}
                      style={{ width: `${v}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Recommended Actions */}
        <div className="modal-section">
          <h3>Recommended Actions</h3>
          {data.recommended_actions?.map((a, i) => (
            <div key={i} className="action-item">→ {a}</div>
          ))}
        </div>

        {/* Download PDF */}
        <button
          className="btn-primary"
          style={{ width: '100%', justifyContent: 'center', marginTop: 8 }}
          onClick={() => window.open(`${API}/vendors/${vendorId}/pdf`, '_blank')}
        >
          <Download size={16} />
          Download PDF Report
        </button>
      </div>
    </div>
  );
}
// ── CSV Import Component ──────────────────────────────────────
function CSVImport({ onImportDone }) {
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState(null);
  const [dragover, setDragover] = useState(false);
  const fileRef = React.useRef();

  const handleFile = async (file) => {
    if (!file) return;
    if (!file.name.endsWith('.csv')) {
      alert('Please upload a CSV file!');
      return;
    }

    setImporting(true);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post(
        `${API}/vendors/import-csv`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      setResult(res.data);
      await onImportDone();
    } catch (e) {
      setResult({ error: 'Import failed. Please check your CSV format.' });
    }
    setImporting(false);
  };

  return (
    <div className="csv-section">
      <h2>📂 Bulk Import Vendors via CSV</h2>
      <p>
        Import hundreds of vendors at once.
        CSV columns: <strong>name, website, industry</strong>
      </p>

      {/* Drop Zone */}
      <div
        className={`csv-upload-area ${dragover ? 'dragover' : ''}`}
        onClick={() => fileRef.current.click()}
        onDragOver={e => { e.preventDefault(); setDragover(true); }}
        onDragLeave={() => setDragover(false)}
        onDrop={e => {
          e.preventDefault();
          setDragover(false);
          handleFile(e.dataTransfer.files[0]);
        }}
      >
        <input
          ref={fileRef}
          type="file"
          accept=".csv"
          onChange={e => handleFile(e.target.files[0])}
        />
        <div className="csv-upload-icon">📄</div>
        <div className="csv-upload-text">
          {importing
            ? '⏳ Importing vendors...'
            : <>Drop your CSV here or <span>browse to upload</span></>
          }
        </div>
      </div>

      {/* Buttons */}
      <div className="csv-buttons">
        <button
          className="btn-primary"
          onClick={() => fileRef.current.click()}
          disabled={importing}
        >
          <Upload size={14} />
          {importing ? 'Importing...' : 'Choose CSV File'}
        </button>
        <button
          className="btn-scan"
          onClick={() => window.open(`${API}/vendors/csv-template`, '_blank')}
        >
          📥 Download Template
        </button>
      </div>

      {/* Result */}
      {result && (
        <div className="import-result">
          {result.error ? (
            <div style={{ color: '#f87171' }}>❌ {result.error}</div>
          ) : (
            <>
              <div className="success">
                ✅ Successfully imported {result.imported} vendors!
              </div>
              {result.skipped > 0 && (
                <div className="warning">
                  ⚠ Skipped {result.skipped} (already exist or empty)
                </div>
              )}
              {result.imported_vendors?.length > 0 && (
                <div className="vendors-list">
                  Imported: {result.imported_vendors.join(', ')}
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
// ── Main App ──────────────────────────────────────────────────
export default function App() {
  const [vendors, setVendors] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [showAlerts, setShowAlerts] = useState(false);
  const [scanningId, setScanningId] = useState(null);
  const [scanningAll, setScanningAll] = useState(false);
  const [modalData, setModalData] = useState(null);
  const [modalVendorId, setModalVendorId] = useState(null);
  const [historyData, setHistoryData] = useState({});
  const [sortByRisk, setSortByRisk] = useState(true);
  const [scanProgress, setScanProgress] = useState('');
  const [form, setForm] = useState({
    name: '', website: '', industry: ''
  });
  const [adding, setAdding] = useState(false);

  const loadVendors = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/vendors`);
      setVendors(res.data.vendors);
    } catch (e) { console.error(e); }
  }, []);

  const loadAlerts = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/alerts`);
      setAlerts(res.data.alerts);
    } catch (e) { console.error(e); }
  }, []);

  useEffect(() => {
    loadVendors();
    loadAlerts();
  }, [loadVendors, loadAlerts]);

  const addVendor = async () => {
    if (!form.name.trim()) return;
    setAdding(true);
    try {
      await axios.post(`${API}/vendors`, form);
      setForm({ name: '', website: '', industry: '' });
      await loadVendors();
    } catch (e) { console.error(e); }
    setAdding(false);
  };

  const deleteVendor = async (id) => {
    if (!window.confirm('Delete this vendor?')) return;
    try {
      await axios.delete(`${API}/vendors/${id}`);
      await loadVendors();
    } catch (e) { console.error(e); }
  };

  const scanVendor = async (vendor) => {
    setScanningId(vendor.id);
    setScanProgress(`Scanning ${vendor.name}... collecting live web data`);
    try {
      const res = await axios.post(
        `${API}/vendors/${vendor.id}/scan`,
        {},
        { timeout: 600000 }
      );
      setModalData(res.data);
      setModalVendorId(vendor.id);
      await loadVendors();
      await loadAlerts();
      const hist = await axios.get(`${API}/vendors/${vendor.id}/history`);
      setHistoryData(prev => ({
        ...prev,
        [vendor.id]: hist.data.history
      }));
    } catch (e) { console.error(e); }
    setScanningId(null);
    setScanProgress('');
  };

  // Rescan all vendors one by one
  const rescanAll = async () => {
    setScanningAll(true);
    for (const vendor of vendors) {
      setScanProgress(`Scanning ${vendor.name}...`);
      setScanningId(vendor.id);
      try {
        await axios.post(
          `${API}/vendors/${vendor.id}/scan`,
          {},
          { timeout: 120000 }
        );
        await loadVendors();
        await loadAlerts();
      } catch (e) { console.error(e); }
      setScanningId(null);
    }
    setScanningAll(false);
    setScanProgress('');
  };

  // Sort vendors by risk score
  const sortedVendors = [...vendors].sort((a, b) => {
    if (!sortByRisk) return 0;
    const scoreA = a.latest_score ?? -1;
    const scoreB = b.latest_score ?? -1;
    return scoreB - scoreA;
  });

  // Stats
  const totalVendors = vendors.length;
  const redCount = vendors.filter(v => v.latest_score >= 61).length;
  const yellowCount = vendors.filter(
    v => v.latest_score >= 31 && v.latest_score < 61
  ).length;
  
  const avgScore = vendors.length > 0
    ? Math.round(
        vendors
          .filter(v => v.latest_score !== null)
          .reduce((sum, v) => sum + v.latest_score, 0) /
        Math.max(vendors.filter(v => v.latest_score !== null).length, 1)
      )
    : 0;

  return (
    <div className="app">
      {/* NAVBAR */}
      <nav className="navbar">
        <div className="navbar-brand">
          <Shield size={26} color="#60a5fa" />
          <h1>VendorGuard AI</h1>
          <span>
            <div className="live-badge">
              <div className="live-dot" />
              LIVE
            </div>
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <button
            className="navbar-alerts"
            onClick={() => setShowAlerts(!showAlerts)}
          >
            <Bell size={16} />
            Alerts
            {alerts.length > 0 && (
              <span className="alert-badge">{alerts.length}</span>
            )}
          </button>
        </div>
      </nav>

      <div className="main-content">

        {/* SCAN PROGRESS BAR */}
        {scanProgress && (
          <div className="scan-progress">
            <RefreshCw size={16} />
            {scanProgress} — collecting data from internet + Wikipedia + AI analysis...
          </div>
        )}

        {/* STATS ROW */}
        <div className="stats-row">
          <div className="stat-card">
            <div className="stat-label">Total Vendors</div>
            <div className="stat-value">{totalVendors}</div>
            <div className="stat-sub">Being monitored</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">🔴 Critical Risk</div>
            <div className="stat-value" style={{ color: '#f87171' }}>
              {redCount}
            </div>
            <div className="stat-sub">Score 61-100</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">🟡 Medium Risk</div>
            <div className="stat-value" style={{ color: '#fbbf24' }}>
              {yellowCount}
            </div>
            <div className="stat-sub">Score 31-60</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Average Score</div>
            <div className="stat-value" style={{
              color: getRiskClass(avgScore) === 'red' ? '#f87171'
                : getRiskClass(avgScore) === 'yellow' ? '#fbbf24'
                  : '#34d399'
            }}>
              {avgScore || '—'}
            </div>
            <div className="stat-sub">Across all vendors</div>
          </div>
        </div>

        {/* ALERTS PANEL */}
        {showAlerts && alerts.length > 0 && (
          <div className="alerts-panel">
            <h2>🔔 Recent Alerts</h2>
            {alerts.map(a => (
              <div key={a.id} className={`alert-item ${a.severity}`}>
                <div>
                  <div>{a.message}</div>
                  <div className="alert-time">
                    {new Date(a.created_at).toLocaleString()}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
  {/* CSV IMPORT */}
        <CSVImport onImportDone={loadVendors} />
        {/* ADD VENDOR */}
        <div className="add-vendor-section">
          <h2>+ Monitor a New Vendor</h2>
          <div className="add-vendor-form">
            <input
              placeholder="Company name (e.g. Stripe)"
              value={form.name}
              onChange={e => setForm({ ...form, name: e.target.value })}
              onKeyDown={e => e.key === 'Enter' && addVendor()}
            />
            <input
              placeholder="Website (e.g. https://stripe.com)"
              value={form.website}
              onChange={e => setForm({ ...form, website: e.target.value })}
            />
            <input
              placeholder="Industry (e.g. Payments)"
              value={form.industry}
              onChange={e => setForm({ ...form, industry: e.target.value })}
            />
            <button
              className="btn-primary"
              onClick={addVendor}
              disabled={adding || !form.name.trim()}
            >
              <Plus size={16} />
              {adding ? 'Adding...' : 'Add Vendor'}
            </button>
          </div>
        </div>

        {/* VENDORS TABLE */}
        <div className="vendors-section">
          <div className="sort-bar">
            <span>
              📊 {totalVendors} vendor{totalVendors !== 1 ? 's' : ''} monitored
            </span>
            <div style={{ display: 'flex', gap: 10 }}>
              <button
                className="btn-scan"
                onClick={() => setSortByRisk(!sortByRisk)}
              >
                <ArrowUpDown size={12} />
                {sortByRisk ? 'Sorted by Risk' : 'Sort by Risk'}
              </button>
              <button
                className="btn-rescan-all"
                onClick={rescanAll}
                disabled={scanningAll || vendors.length === 0}
              >
                <RefreshCw size={12} />
                {scanningAll ? 'Scanning All...' : 'Rescan All'}
              </button>
            </div>
          </div>

          {vendors.length === 0 ? (
            <div className="empty-state">
              <Shield size={56} color="#1e2433" />
              <p style={{ fontSize: 16, marginTop: 16, color: '#4a5568' }}>
                No vendors monitored yet
              </p>
              <p style={{ fontSize: 13, marginTop: 8, color: '#2d3748' }}>
                Add your first vendor above to start monitoring risk in real time
              </p>
            </div>
          ) : (
            <table className="vendor-table">
              <thead>
                <tr>
                  <th>Vendor</th>
                  <th>Industry</th>
                  <th>Risk Score</th>
                  <th>Status</th>
                  <th>Last Scanned</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {sortedVendors.map(vendor => {
                  const cls = getRiskClass(vendor.latest_score);
                  const isScanning = scanningId === vendor.id;
                  const history = historyData[vendor.id] || [];

                  return (
                    <tr key={vendor.id}>
                      <td>
                        <div
                          className="vendor-name"
                          onClick={() => {
                            if (vendor.latest_score !== null) {
                              setModalData({
                                vendor_name: vendor.name,
                                risk_score: vendor.latest_score,
                                risk_level: cls.toUpperCase(),
                                summary: 'Click Scan Now for full analysis.',
                                key_findings: [],
                                risk_categories: {},
                                recommended_actions: [],
                                confidence_level: 'N/A',
                                signals_found: 0,
                                score_change: 0
                              });
                              setModalVendorId(vendor.id);
                            }
                          }}
                        >
                          {vendor.name}
                        </div>
                        <div style={{ fontSize: 12, color: '#4a5568' }}>
                          {vendor.website}
                        </div>
                      </td>
                      <td style={{ color: '#64748b', fontSize: 13 }}>
                        {vendor.industry || '—'}
                      </td>
                      <td>
                        {vendor.latest_score !== null ? (
                          <div className="score-bar-wrap">
                            <div className="score-bar">
                              <div
                                className={`score-bar-fill ${cls}`}
                                style={{ width: `${vendor.latest_score}%` }}
                              />
                            </div>
                            <span className="score-number" style={{
                              color: cls === 'red' ? '#f87171'
                                : cls === 'yellow' ? '#fbbf24' : '#34d399'
                            }}>
                              {vendor.latest_score}
                            </span>
                          </div>
                        ) : (
                          <span style={{ color: '#2d3748', fontSize: 13 }}>
                            Not scanned yet
                          </span>
                        )}
                        {history.length > 1 && (
                          <div style={{ height: 36, marginTop: 4 }}>
                            <ResponsiveContainer width="100%" height={36}>
                              <LineChart data={history}>
                                <Line
                                  type="monotone"
                                  dataKey="score"
                                  stroke={
                                    cls === 'red' ? '#f87171'
                                      : cls === 'yellow' ? '#fbbf24'
                                        : '#34d399'
                                  }
                                  dot={false}
                                  strokeWidth={2}
                                />
                              </LineChart>
                            </ResponsiveContainer>
                          </div>
                        )}
                      </td>
                      <td>
                        {isScanning ? (
                          <span className="scanning-text">
                            <RefreshCw size={12} /> Scanning...
                          </span>
                        ) : vendor.latest_score !== null ? (
                          <span className={`risk-badge ${cls}`}>
                            {getRiskIcon(cls)}
                            {cls.toUpperCase()}
                          </span>
                        ) : (
                          <span className="risk-badge none">PENDING</span>
                        )}
                      </td>
                      <td style={{ fontSize: 12, color: '#4a5568' }}>
                        {vendor.last_scanned
                          ? new Date(vendor.last_scanned).toLocaleString()
                          : 'Never'}
                      </td>
                      <td>
                        <button
                          className="btn-scan"
                          onClick={() => scanVendor(vendor)}
                          disabled={isScanning || scanningAll}
                        >
                          <RefreshCw size={12} />
                          {isScanning ? 'Scanning...' : 'Scan Now'}
                        </button>
                        <button
                          className="btn-scan"
                          style={{
                            marginLeft: 6,
                            background: '#1a2e1a',
                            borderColor: '#34d399',
                            color: '#34d399'
                          }}
                          onClick={() => window.open(
                            `${API}/vendors/${vendor.id}/pdf`, '_blank'
                          )}
                          disabled={!vendor.latest_score}
                        >
                          <Download size={12} />
                          PDF
                        </button>
                        <button
                          className="btn-delete"
                          onClick={() => deleteVendor(vendor.id)}
                          disabled={isScanning}
                        >
                          <Trash2 size={12} />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* FOOTER */}
      <div className="app-footer">
        VendorGuard AI — Powered by Bright Data + Groq AI •
        Built for Web Data UNLOCKED Hackathon 2026
      </div>

      {/* RISK REPORT MODAL */}
      {modalData && (
        <RiskModal
          data={modalData}
          vendorId={modalVendorId}
          onClose={() => {
            setModalData(null);
            setModalVendorId(null);
          }}
        />
      )}
    </div>
  );
}