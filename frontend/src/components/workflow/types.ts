export interface WorkflowState {
  id: string;
  label: string;
  description: string;
  color: string;
  icon: string;
  category: 'initial' | 'active' | 'terminal' | 'success' | 'failure';
}

export interface WorkflowTransition {
  from: string;
  to: string;
  label: string;
  description: string;
  action: string;
  roles: string[];
  requiresConfirmation: boolean;
  requiresForm: boolean;
  formConfig?: WorkflowFormConfig;
  sideEffects?: WorkflowSideEffect[];
  businessRules?: string[];
}

export interface WorkflowFormConfig {
  title: string;
  fields: WorkflowFormField[];
}

export interface WorkflowFormField {
  name: string;
  label: string;
  type: 'text' | 'textarea' | 'select' | 'number' | 'toggle' | 'file' | 'rating';
  required: boolean;
  placeholder?: string;
  options?: { value: string; label: string }[];
  validation?: { min?: number; max?: number; pattern?: string; message?: string };
}

export interface WorkflowSideEffect {
  type: 'notification' | 'email' | 'push' | 'sms' | 'ai_analysis' | 'audit_log' | 'auto_assignment' | 'priority_calculation' | 'file_upload' | 'capacity_check' | 'sla_check' | 'escalation_check';
  description: string;
  target?: string;
}

export interface WorkflowStep {
  state: WorkflowState;
  transitions: WorkflowTransition[];
  data?: any;
}

export interface WorkflowDefinition {
  id: string;
  name: string;
  description: string;
  states: Record<string, WorkflowState>;
  transitions: WorkflowTransition[];
  initialState: string;
  terminalStates: string[];
  roles: string[];
}
