import { useState } from 'react';
import type { WorkflowFormField } from './types';

interface WizardStep {
  id: string;
  title: string;
  description: string;
  fields: WorkflowFormField[];
}

interface WorkflowWizardProps {
  steps: WizardStep[];
  onComplete: (data: Record<string, any>) => void;
  initialData?: Record<string, any>;
  loading?: boolean;
}

export default function WorkflowWizard({ steps, onComplete, initialData, loading }: WorkflowWizardProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [data, setData] = useState<Record<string, any>>(initialData || {});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [completed, setCompleted] = useState(false);

  const totalSteps = steps.length;
  const progressPercent = ((currentStep + 1) / totalSteps) * 100;
  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === totalSteps - 1;
  const isSummaryStep = currentStep === totalSteps;

  const validateStep = (stepIndex: number): boolean => {
    const step = steps[stepIndex];
    const newErrors: Record<string, string> = {};
    for (const field of step.fields) {
      if (field.required && !data[field.name]) {
        newErrors[field.name] = `${field.label} is required`;
      }
      if (field.validation) {
        const val = data[field.name];
        if (field.validation.min !== undefined && Number(val) < field.validation.min) {
          newErrors[field.name] = field.validation.message || `Minimum value is ${field.validation.min}`;
        }
        if (field.validation.max !== undefined && Number(val) > field.validation.max) {
          newErrors[field.name] = field.validation.message || `Maximum value is ${field.validation.max}`;
        }
        if (field.validation.pattern && val && !new RegExp(field.validation.pattern).test(val)) {
          newErrors[field.name] = field.validation.message || 'Invalid format';
        }
      }
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (!validateStep(currentStep)) return;
    if (isLastStep) {
      setCurrentStep(totalSteps);
    } else {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep((prev) => prev - 1);
    }
  };

  const handleComplete = () => {
    setCompleted(true);
    setTimeout(() => onComplete(data), 800);
  };

  const handleFieldChange = (field: WorkflowFormField, value: any) => {
    setData((prev) => ({ ...prev, [field.name]: value }));
    if (errors[field.name]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[field.name];
        return next;
      });
    }
  };

  const renderField = (field: WorkflowFormField) => {
    const value = data[field.name] !== undefined ? data[field.name] : '';
    const error = errors[field.name];

    switch (field.type) {
      case 'textarea':
        return (
          <div key={field.name}>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {field.label}{field.required && <span className="text-red-500 ml-0.5">*</span>}
            </label>
            <textarea
              value={value}
              onChange={(e) => handleFieldChange(field, e.target.value)}
              placeholder={field.placeholder}
              rows={3}
              className={`w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${error ? 'border-red-300 bg-red-50' : 'border-gray-300'}`}
            />
            {error && <p className="text-xs text-red-500 mt-0.5">{error}</p>}
          </div>
        );
      case 'select':
        return (
          <div key={field.name}>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {field.label}{field.required && <span className="text-red-500 ml-0.5">*</span>}
            </label>
            <select
              value={value}
              onChange={(e) => handleFieldChange(field, e.target.value)}
              className={`w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${error ? 'border-red-300 bg-red-50' : 'border-gray-300'}`}
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
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {field.label}{field.required && <span className="text-red-500 ml-0.5">*</span>}
            </label>
            <input
              type="number"
              value={value}
              onChange={(e) => handleFieldChange(field, e.target.value)}
              placeholder={field.placeholder}
              className={`w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${error ? 'border-red-300 bg-red-50' : 'border-gray-300'}`}
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
                onChange={(e) => handleFieldChange(field, e.target.checked)}
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
            <label className="block text-sm font-medium text-gray-700 mb-1">{field.label}</label>
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => handleFieldChange(field, star)}
                  className={`text-2xl transition-colors ${Number(value) >= star ? 'text-yellow-400' : 'text-gray-300 hover:text-yellow-300'}`}
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
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {field.label}{field.required && <span className="text-red-500 ml-0.5">*</span>}
            </label>
            <input
              type="file"
              onChange={(e) => handleFieldChange(field, e.target.files?.[0])}
              className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
            {error && <p className="text-xs text-red-500 mt-0.5">{error}</p>}
          </div>
        );
      default:
        return (
          <div key={field.name}>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {field.label}{field.required && <span className="text-red-500 ml-0.5">*</span>}
            </label>
            <input
              type="text"
              value={value}
              onChange={(e) => handleFieldChange(field, e.target.value)}
              placeholder={field.placeholder}
              className={`w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 ${error ? 'border-red-300 bg-red-50' : 'border-gray-300'}`}
            />
            {error && <p className="text-xs text-red-500 mt-0.5">{error}</p>}
          </div>
        );
    }
  };

  if (completed) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
        <div className="mb-4">
          <div className="mx-auto h-16 w-16 rounded-full bg-green-100 flex items-center justify-center">
            <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-1">Complete!</h3>
        <p className="text-sm text-gray-500">All steps have been completed successfully.</p>
        <div className="mt-4">
          <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div className="h-full bg-green-500 rounded-full animate-pulse" style={{ width: '100%' }} />
          </div>
        </div>
      </div>
    );
  }

  if (isSummaryStep) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h3 className="text-sm font-semibold text-gray-900 mb-4">Review & Confirm</h3>
        <div className="space-y-4">
          {steps.map((step) => {
            const stepFields = step.fields.filter((f) => data[f.name] !== undefined && data[f.name] !== '');
            if (stepFields.length === 0) return null;
            return (
              <div key={step.id} className="border border-gray-200 rounded-lg p-3">
                <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">{step.title}</h4>
                <div className="space-y-2">
                  {stepFields.map((field) => {
                    const value = data[field.name];
                    const displayValue = field.type === 'file'
                      ? (value?.name || 'File attached')
                      : field.type === 'toggle'
                      ? (value ? 'Yes' : 'No')
                      : field.type === 'rating'
                      ? `${value} / 5`
                      : field.options
                      ? field.options.find((o) => o.value === value)?.label || value
                      : value;
                    return (
                      <div key={field.name} className="flex items-start justify-between">
                        <span className="text-xs text-gray-500">{field.label}</span>
                        <span className="text-sm font-medium text-gray-900 text-right max-w-[60%] truncate">{displayValue || <span className="text-gray-300 italic">Not provided</span>}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
        <div className="flex gap-3 justify-between mt-6 pt-4 border-t border-gray-200">
          <button
            onClick={handleBack}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Back
          </button>
          <button
            onClick={handleComplete}
            disabled={loading}
            className="px-6 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? 'Processing...' : (
              <>
                Complete
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
              </>
            )}
          </button>
        </div>
      </div>
    );
  }

  const step = steps[currentStep];

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5">
      <div className="flex items-center justify-between mb-1">
        <h3 className="text-sm font-semibold text-gray-900">{step.title}</h3>
        <span className="text-xs text-gray-500">Step {currentStep + 1} of {totalSteps}</span>
      </div>
      <p className="text-xs text-gray-500 mb-4">{step.description}</p>

      <div className="h-1.5 bg-gray-100 rounded-full mb-5 overflow-hidden">
        <div className="h-full bg-blue-500 rounded-full transition-all duration-500" style={{ width: `${progressPercent}%` }} />
      </div>

      <div className="flex gap-2 mb-5">
        {steps.map((s, idx) => {
          const isActive = idx === currentStep;
          const isDone = idx < currentStep;
          return (
            <div key={s.id} className="flex items-center gap-2">
              <div className={`h-6 w-6 rounded-full flex items-center justify-center text-xs font-medium flex-shrink-0 ${
                isDone ? 'bg-green-500 text-white' :
                isActive ? 'bg-blue-600 text-white ring-2 ring-blue-200' :
                'bg-gray-200 text-gray-500'
              }`}>
                {isDone ? (
                  <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" /></svg>
                ) : idx + 1}
              </div>
              <span className={`text-xs hidden sm:inline ${isActive ? 'font-medium text-blue-700' : isDone ? 'text-green-700' : 'text-gray-400'}`}>{s.title}</span>
              {idx < steps.length - 1 && (
                <div className={`h-0.5 w-6 hidden sm:block ${isDone ? 'bg-green-400' : 'bg-gray-200'}`} />
              )}
            </div>
          );
        })}
      </div>

      <div className="space-y-4 mb-6">
        {step.fields.map((field) => renderField(field))}
      </div>

      <div className="flex gap-3 justify-between pt-4 border-t border-gray-200">
        <button
          onClick={handleBack}
          disabled={isFirstStep}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Back
        </button>
        <button
          onClick={handleNext}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          {isLastStep ? 'Review' : 'Next'}
          {!isLastStep && (
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
          )}
        </button>
      </div>
    </div>
  );
}
