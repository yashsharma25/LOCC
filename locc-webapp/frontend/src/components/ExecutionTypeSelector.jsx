import React, { useState } from 'react';
import API from '../api';

export default function ExecutionTypeSelector() {
  const [executionType, setExecutionType] = useState('');

  const handleSubmit = async () => {
    if (!executionType) {
      alert('Please select an execution type');
      return;
    }

    try {
      const res = await API.post('/set_execution_type', { execution_type: executionType });
      alert(res.data.message);
    } catch (err) {
      alert('Failed to set execution type: ' + err.message);
    }
  };

  return (
    <div>
      <h2>Execution Type</h2>
      <select value={executionType} onChange={(e) => setExecutionType(e.target.value)}>
        <option value="">-- Select Execution Type --</option>
        <option value="upper bound">Upper Bound</option>
        <option value="lower bound">Lower Bound</option>
      </select>
      <button onClick={handleSubmit}>Set Execution Type</button>
    </div>
  );
}
