import React, { useState } from 'react';
import API from '../api';

export default function LOCCProtocolForm() {
  const [steps, setSteps] = useState([
    { operation_type: '', operator_choice: '', party_index: '', qudit_index: '', condition: '' }
  ]);

  const handleChange = (index, field, value) => {
    const newSteps = [...steps];
    newSteps[index][field] = value;
    setSteps(newSteps);
  };

  const addStep = () => {
    setSteps([...steps, { operation_type: '', operator_choice: '', party_index: '', qudit_index: '', condition: '' }]);
  };

  const submitSteps = async () => {
    for (const step of steps) {
      const { operation_type, operator_choice, party_index, qudit_index, condition } = step;

      const parsedCondition =
        operation_type === 'conditional_operation' && condition
          ? condition.split(',').map(Number)
          : null;

      const payload = {
        operation_type,
        operator_choice,
        party_index: parseInt(party_index),
        qudit_index: parseInt(qudit_index),
        condition: parsedCondition,
      };

      try {
        const res = await API.post('/add_locc_operation', payload);
        alert(res.data.message);
      } catch (err) {
        alert('Failed to add LOCC step: ' + err.message);
      }
    }
  };

  return (
    <div>
      <h2>LOCC Protocol Steps</h2>
      {steps.map((step, i) => (
        <div key={i} style={{ marginBottom: '1em' }}>
          <input
            placeholder="operation_type"
            value={step.operation_type}
            onChange={e => handleChange(i, 'operation_type', e.target.value)}
          />
          <input
            placeholder="operator_choice"
            value={step.operator_choice}
            onChange={e => handleChange(i, 'operator_choice', e.target.value)}
          />
          <input
            placeholder="party_index"
            value={step.party_index}
            onChange={e => handleChange(i, 'party_index', e.target.value)}
          />
          <input
            placeholder="qudit_index"
            value={step.qudit_index}
            onChange={e => handleChange(i, 'qudit_index', e.target.value)}
          />
          <input
            placeholder="condition (e.g. 0,1,1)"
            value={step.condition}
            onChange={e => handleChange(i, 'condition', e.target.value)}
          />
        </div>
      ))}
      <button onClick={addStep}>Add Step</button>
      <button onClick={submitSteps}>Submit LOCC Protocol</button>
    </div>
  );
}
