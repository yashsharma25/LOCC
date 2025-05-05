import React, { useState } from 'react';
import API from '../api';

export default function QuantumStateForm() {
  const [rows, setRows] = useState([{ amplitude: '', basis: '' }]);

  const handleChange = (index, field, value) => {
    const newRows = [...rows];
    newRows[index][field] = value;
    setRows(newRows);
  };

  const addRow = () => setRows([...rows, { amplitude: '', basis: '' }]);

  const submitState = async () => {
    const amplitudes = rows.map(r => eval(r.amplitude));
    const basis_states = rows.map(r => r.basis);
    const res = await API.post('/create_state', { amplitudes, basis_states });
    alert(res.data.message);
  };

  return (
    <div>
      <h2>Quantum State Input</h2>
      {rows.map((row, i) => (
        <div key={i}>
          <input
            value={row.amplitude}
            onChange={e => handleChange(i, 'amplitude', e.target.value)}
            placeholder="Amplitude (e.g., 1/np.sqrt(2))"
          />
          <input
            value={row.basis}
            onChange={e => handleChange(i, 'basis', e.target.value)}
            placeholder="Basis State (e.g., 00)"
          />
        </div>
      ))}
      <button onClick={addRow}>Add Row</button>
      <button onClick={submitState}>Submit State</button>
    </div>
  );
}
