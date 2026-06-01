import { useState } from 'react';
import type { WorkflowDefinition, WorkflowTransition, WorkflowFormField } from './types';
import Modal from '../ui/Modal';

interface WorkflowActionPanelProps {
  workflow: WorkflowDefinition;
  currentState: string;
  userRole: string;
  onAction: (actionId: string, formData?: Record<string, any>) => void;
  loading?: boolean;
}

const sideEffectIcons: Record<string, string> = {
  notification: '🔔',
  email: '📧',
  push: '📱',
  sms: '💬',
  whatsapp: '💬',
  ai_analysis: '🤖',
  audit_log: '📋',
  auto_assignment: '👤',
  priority_calculation: '⚡',
  file_upload: '📎',
  capacity_check: '📊',
  sla_check: '⏱️',
  escalation_check: '⚠️',
};

const stateColorBg: Record<string, string> = {
  gray: 'bg-gray-100',
  yellow: 'bg-yellow-100',
  blue: 'bg-blue-100',
  indigo: 'bg-indigo-100',
  purple: 'bg-purple-100',
  green: 'bg-green-100',
  red: 'bg-red-100',
};

const stateColorBadge: Record<string, string> = {
  gray: 'bg-gray-500',
  yellow: 'bg-yellow-500',
  blue: 'bg-blue-500',
  indigo: 'bg-indigo-500',
  purple: 'bg-purple-500',
  green: 'bg-green-500',
  red: 'bg-red-500',
};



export default function WorkflowActionPanel({ workflow, currentState, userRole, onAction, loading }: WorkflowActionPanelProps) {
  const [confirmTransition, setConfirmTransition] = useState<WorkflowTransition | null>(null);
  const [formTransition, setFormTransition] = useState<WorkflowTransition | null>(null);
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  const currentStateDef = workflow.states[currentState];
  const isTerminal = workflow.terminalStates.includes(currentState);

  const availableTransitions = workflow.transitions.filter(
    (t) => t.from === currentState && t.roles.includes(userRole)
  );

  const disabledTransitions = workflow.transitions.filter(
    (t) => t.from === currentState && !t.roles.includes(userRole)
  );

  const handleFormSubmit = () => {
    if (!formTransition) return;
    const errors: Record<string, string> = {};
    if (formTransition.formConfig) {
      for (const field of formTransition.formConfig.fields) {
        if (field.required && !formData[field.name]) {
          errors[field.name] = `${field.label} is required`;
        }
        if (field.validation) {
          const val = formData[field.name];
          if (field.validation.min !== undefined && Number(val) < field.validation.min) {
            errors[field.name] = field.validation.message || `Minimum value is ${field.validation.min}`;
          }
          if (field.validation.max !== undefined && Number(val) > field.validation.max) {
            errors[field.name] = field.validation.message || `Maximum value is ${field.validation.max}`;
          }
          if (field.validation.pattern && val && !new RegExp(field.validation.pattern).test(val)) {
            errors[field.name] = field.validation.message || 'Invalid format';
          }
        }
      }
    }
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }
    onAction(formTransition.to, formData);
    setFormTransition(null);
    setFormData({});
    setFormErrors({});
  };

  const handleConfirm = () => {
    if (confirmTransition) {
      onAction(confirmTransition.to);
      setConfirmTransition(null);
    }
  };

  const handleDirectAction = (transition: WorkflowTransition) => {
    onAction(transition.to);
  };

  const handleFormFieldChange = (field: WorkflowFormField, value: any) => {
    setFormData((prev) => ({ ...prev, [field.name]: value }));
    if (formErrors[field.name]) {
      setFormErrors((prev) => {
        const next = { ...prev };
        delete next[field.name];
        return next;
      });
    }
  };

  const renderFormField = (field: WorkflowFormField) => {
    const value = formData[field.name] || '';
    const error = formErrors[field.name];

    switch (field.type) {
      case 'textarea':
        return (
          <div key={field.name}>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              {field.label}{field.required && <span className="text-red-500 ml-0.5">*</span>}
            </label>
            <textarea
              value={value}
              onChange={(e) => handleFormFieldChange(field, e.target.value)}
              placeholder={field.placeholder}
              rows={3}
              className={`w-full text-sm border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 ${error ? 'border-red-300 bg-red-50' : 'border-gray-300'}`}
            />
            {error && <p className="text-xs text-red-500 mt-0.5">{error}</p>}
          </div>
        );
      case 'select':
        return (
          <div key={field.name}>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              {field.label}{field.required && <span className="text-red-500 ml-0.5">*</span>}
            </label>
            <select
              value={value}
              onChange={(e) => handleFormFieldChange(field, e.target.value)}
              className={`w-full text-sm border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 ${error ? 'border-red-300 bg-red-50' : 'border-gray-300'}`}
            >
              <option value="">{field.placeholder || 'Select...'}</option>
              {field.options?.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
            {error && <p className="text-xs text-red-500 mt-0.5">{error}</p>}
          </div>
        );
      case 'number':
        return (
          <div key={field.name}>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              {field.label}{field.required && <span className="text-red-500 ml-0.5">*</span>}
            </label>
            <input
              type="number"
              value={value}
              onChange={(e) => handleFormFieldChange(field, e.target.value)}
              placeholder={field.placeholder}
              className={`w-full text-sm border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 ${error ? 'border-red-300 bg-red-50' : 'border-gray-300'}`}
            />
            {error && <p className="text-xs text-red-500 mt-0.5">{error}</p>}
          </div>
        );
      case 'toggle':
        return (
          <div key={field.name} className="flex items-center gap-3">
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={!!value}
                onChange={(e) => handleFormFieldChange(field, e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600" />
            </label>
            <span className="text-sm text-gray-700">{field.label}</span>
          </div>
        );
      case 'rating':
        return (
          <div key={field.name}>
            <label className="block text-xs font-medium text-gray-700 mb-1">{field.label}</label>
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => handleFormFieldChange(field, star)}
                  className={`text-xl transition-colors ${Number(value) >= star ? 'text-yellow-400' : 'text-gray-300 hover:text-yellow-300'}`}
                >
                  ★
                </button>
              ))}
            </div>
          </div>
        );
      case 'file':
        return (
          <div key={field.name}>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              {field.label}{field.required && <span className="text-red-500 ml-0.5">*</span>}
            </label>
            <input
              type="file"
              onChange={(e) => handleFormFieldChange(field, e.target.files?.[0])}
              className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
            {error && <p className="text-xs text-red-500 mt-0.5">{error}</p>}
          </div>
        );
      default:
        return (
          <div key={field.name}>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              {field.label}{field.required && <span className="text-red-500 ml-0.5">*</span>}
            </label>
            <input
              type="text"
              value={value}
              onChange={(e) => handleFormFieldChange(field, e.target.value)}
              placeholder={field.placeholder}
              className={`w-full text-sm border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 ${error ? 'border-red-300 bg-red-50' : 'border-gray-300'}`}
            />
            {error && <p className="text-xs text-red-500 mt-0.5">{error}</p>}
          </div>
        );
    }
  };

  if (!currentStateDef) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <p className="text-sm text-gray-500">Unknown workflow state: {currentState}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5">
      <div className="flex items-center gap-3 mb-5">
        <div className={`h-10 w-10 rounded-full flex items-center justify-center text-lg ${stateColorBg[currentStateDef.color] || 'bg-gray-100'}`}>
          {currentStateDef.icon}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-semibold text-gray-900">{currentStateDef.label}</h3>
            <span className={`h-2.5 w-2.5 rounded-full ${stateColorBadge[currentStateDef.color] || 'bg-gray-400'}`} />
          </div>
          <p className="text-xs text-gray-500">{currentStateDef.description}</p>
        </div>
      </div>

      {isTerminal && (
        <div className="mb-4 p-3 bg-gray-50 border border-gray-200 rounded-lg">
          <div className="flex items-center gap-2">
            <span className="text-lg">🔒</span>
            <span className="text-sm font-medium text-gray-700">Terminal State</span>
          </div>
          <p className="text-xs text-gray-500 mt-1">This signal has reached a terminal state. No further actions can be performed.</p>
        </div>
      )}

      <div className="space-y-2">
        {availableTransitions.map((transition) => {
          const toState = workflow.states[transition.to];
          const isDestructive = transition.label === 'Cancel' || transition.label === 'Reject';

          return (
            <div
              key={`${transition.from}-${transition.to}`}
              className="border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
            >
              <button
                onClick={() => {
                  if (transition.requiresForm) {
                    setFormTransition(transition);
                    setFormData({});
                    setFormErrors({});
                  } else if (transition.requiresConfirmation) {
                    setConfirmTransition(transition);
                  } else {
                    handleDirectAction(transition);
                  }
                }}
                disabled={loading}
                className={`w-full text-left p-3 rounded-lg transition-all ${isDestructive ? 'hover:bg-red-50' : 'hover:bg-gray-50'} disabled:opacity-50`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`text-sm font-medium ${isDestructive ? 'text-red-700' : 'text-gray-900'}`}>{transition.label}</span>
                    {toState && (
                      <span className="text-xs text-gray-400 flex items-center gap-1">
                        → <span className={`inline-block h-2 w-2 rounded-full ${stateColorBadge[toState.color] || 'bg-gray-400'}`} /> {toState.label}
                      </span>
                    )}
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-0.5">{transition.description}</p>

                {transition.sideEffects && transition.sideEffects.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {transition.sideEffects.map((effect, ei) => (
                      <span
                        key={ei}
                        className="inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded-full bg-gray-100 text-gray-600"
                        title={effect.description}
                      >
                        <span>{sideEffectIcons[effect.type] || '•'}</span>
                        <span className="truncate max-w-[120px]">{effect.description}</span>
                      </span>
                    ))}
                  </div>
                )}

                {transition.businessRules && transition.businessRules.length > 0 && (
                  <div className="mt-2 space-y-0.5">
                    {transition.businessRules.map((rule, ri) => (
                      <p key={ri} className="text-[10px] text-gray-400 flex items-center gap-1">
                        <svg className="h-3 w-3 text-gray-300 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                        {rule}
                      </p>
                    ))}
                  </div>
                )}
              </button>
            </div>
          );
        })}

        {disabledTransitions.map((transition) => {
          const toState = workflow.states[transition.to];
          return (
            <div
              key={`disabled-${transition.from}-${transition.to}`}
              className="border border-gray-100 rounded-lg opacity-50 cursor-not-allowed"
              title={`Requires role: ${transition.roles.join(', ')}`}
            >
              <div className="p-3">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-gray-400">{transition.label}</span>
                  {toState && (
                    <span className="text-xs text-gray-400 flex items-center gap-1">
                      → {toState.label}
                    </span>
                  )}
                  <svg className="h-3.5 w-3.5 text-gray-300 ml-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m0 0v2m0-2h2m-2 0H10m9-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                </div>
                <p className="text-xs text-gray-400 mt-0.5">{transition.description}</p>
                <p className="text-[10px] text-gray-400 mt-1">Requires: {transition.roles.join(', ')}</p>
              </div>
            </div>
          );
        })}

        {!isTerminal && availableTransitions.length === 0 && disabledTransitions.length === 0 && (
          <div className="p-4 bg-gray-50 border border-dashed border-gray-200 rounded-lg text-center">
            <p className="text-sm text-gray-500">No transitions available</p>
            <p className="text-xs text-gray-400 mt-0.5">No actions are available from this state</p>
          </div>
        )}
      </div>

      <Modal open={!!confirmTransition} onClose={() => setConfirmTransition(null)} title="Confirm Action" size="sm">
        {confirmTransition && (
          <div className="space-y-4">
            <div className="flex items-center gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <span className="text-lg">⚠️</span>
              <p className="text-sm text-yellow-800">
                Are you sure you want to <strong>{confirmTransition.label}</strong> this signal?
              </p>
            </div>
            <p className="text-sm text-gray-600">
              This will move the signal from <strong>{workflow.states[confirmTransition.from]?.label}</strong> to <strong>{workflow.states[confirmTransition.to]?.label}</strong>.
            </p>
            {confirmTransition.sideEffects && confirmTransition.sideEffects.length > 0 && (
              <div>
                <p className="text-xs font-medium text-gray-700 mb-1">This will trigger:</p>
                <ul className="space-y-1">
                  {confirmTransition.sideEffects.map((effect, ei) => (
                    <li key={ei} className="flex items-center gap-1.5 text-xs text-gray-600">
                      <span>{sideEffectIcons[effect.type] || '•'}</span>
                      {effect.description}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <div className="flex gap-3 justify-end pt-2">
              <button
                onClick={() => setConfirmTransition(null)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirm}
                disabled={loading}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Processing...' : 'Confirm'}
              </button>
            </div>
          </div>
        )}
      </Modal>

      <Modal open={!!formTransition} onClose={() => { setFormTransition(null); setFormErrors({}); }} title={formTransition?.formConfig?.title || 'Form'} size="md">
        {formTransition && formTransition.formConfig && (
          <div className="space-y-4">
            <p className="text-sm text-gray-600">{formTransition.description}</p>
            <div className="space-y-3">
              {formTransition.formConfig.fields.map((field) => renderFormField(field))}
            </div>
            {formTransition.sideEffects && formTransition.sideEffects.length > 0 && (
              <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-xs font-medium text-blue-700 mb-1">Side effects:</p>
                <ul className="space-y-1">
                  {formTransition.sideEffects.map((effect, ei) => (
                    <li key={ei} className="flex items-center gap-1.5 text-xs text-blue-600">
                      <span>{sideEffectIcons[effect.type] || '•'}</span>
                      {effect.description}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <div className="flex gap-3 justify-end pt-2 border-t border-gray-200">
              <button
                onClick={() => { setFormTransition(null); setFormErrors({}); }}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleFormSubmit}
                disabled={loading}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Processing...' : formTransition.label}
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
