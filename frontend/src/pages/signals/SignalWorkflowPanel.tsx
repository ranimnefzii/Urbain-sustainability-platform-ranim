import { useState, useEffect, useMemo, useCallback } from 'react';
import { WorkflowTimeline, WorkflowActionPanel, SIGNAL_WORKFLOW, SIGNAL_STATES } from '../../components/workflow';
import { signals, users, sectors, ai } from '../../api/endpoints';
import { useAuth } from '../../contexts/AuthContext';
import { useToast } from '../../contexts/ToastContext';
import Modal from '../../components/ui/Modal';
import type { Signal } from '../../types';

interface Props {
  signal: Signal;
  onRefresh: () => void;
}

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

export default function SignalWorkflowPanel({ signal, onRefresh }: Props) {
  const { user } = useAuth();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [userList, setUserList] = useState<{ id: number; first_name: string; last_name: string; email: string }[]>([]);
  const [sectorList, setSectorList] = useState<{ id: number; name: string }[]>([]);
  const [feedbackModal, setFeedbackModal] = useState(false);
  const [feedbackRating, setFeedbackRating] = useState(5);
  const [feedbackText, setFeedbackText] = useState('');
  const [showFeedbackSection, setShowFeedbackSection] = useState(false);
  const [showAiSuggestion, setShowAiSuggestion] = useState(false);
  const [aiClassifying, setAiClassifying] = useState(false);

  const userRole = user?.role?.toLowerCase() || 'citizen';
  const isOwner = user?.id === signal.created_by_user?.id;
  const hasFeedback = signal.citizen_satisfaction != null;
  const canFeedback = (signal.status === 'RESOLVED' || signal.status === 'CLOSED') && isOwner && !hasFeedback;

  const fetchAssignData = useCallback(async () => {
    try {
      const [usersRes, sectorsRes] = await Promise.all([
        users.list({ size: 100 }),
        sectors.list(),
      ]);
      setUserList(usersRes.data.data?.items ?? []);
      setSectorList(sectorsRes.data.data ?? []);
    } catch {
      toast('Failed to load assign form data', 'error');
    }
  }, [toast]);

  useEffect(() => {
    if (signal.status === 'UNDER_REVIEW' || signal.status === 'ASSIGNED') {
      fetchAssignData();
    }
  }, [signal.status, fetchAssignData]);

  const timelineEntries = useMemo(() => {
    const entries: { stateId: string; timestamp?: string; note?: string }[] = [];
    if (signal.created_at) {
      entries.push({ stateId: signal.status === 'DRAFT' ? 'DRAFT' : 'SUBMITTED', timestamp: signal.created_at, note: 'Signal created' });
    }
    if (signal.assigned_at) entries.push({ stateId: 'ASSIGNED', timestamp: signal.assigned_at });
    if (signal.started_processing_at) entries.push({ stateId: 'IN_PROGRESS', timestamp: signal.started_processing_at });
    if (signal.resolved_at) entries.push({ stateId: 'RESOLVED', timestamp: signal.resolved_at });
    if (signal.closed_at) entries.push({ stateId: 'CLOSED', timestamp: signal.closed_at });
    return entries;
  }, [signal]);

  const baseWorkflow = useMemo(() => ({
    ...SIGNAL_WORKFLOW,
    states: { ...SIGNAL_WORKFLOW.states },
    transitions: SIGNAL_WORKFLOW.transitions.map((t) => ({ ...t, formConfig: t.formConfig ? { ...t.formConfig, fields: t.formConfig.fields.map((f) => ({ ...f })) } : undefined })),
  }), []);

  const hydratedWorkflow = useMemo(() => ({
    ...baseWorkflow,
    transitions: baseWorkflow.transitions.map((t) => {
      if (t.action === 'signals.assign' && t.formConfig) {
        return {
          ...t,
          formConfig: {
            ...t.formConfig,
            fields: t.formConfig.fields.map((f) => {
              if (f.name === 'assigned_to_user_id') {
                return {
                  ...f,
                  options: userList.map((u) => ({
                    value: String(u.id),
                    label: `${u.first_name} ${u.last_name} (${u.email})`,
                  })),
                };
              }
              if (f.name === 'assigned_sector_id') {
                return {
                  ...f,
                  options: sectorList.map((s) => ({
                    value: String(s.id),
                    label: s.name,
                  })),
                };
              }
              return f;
            }),
          },
        };
      }
      return t;
    }),
  }), [baseWorkflow, userList, sectorList]);

  const onAction = useCallback(async (action: string, formData?: Record<string, any>) => {
    const id = signal.id;
    const currentStatus = signal.status;
    setLoading(true);

    try {
      if (action === 'UNDER_REVIEW' && currentStatus === 'SUBMITTED') {
        await signals.process(id);
        toast('Signal moved to under review', 'success');
      } else if (action === 'ASSIGNED') {
        if (!formData?.assigned_to_user_id) {
          toast('Please select a user to assign', 'error');
          setLoading(false);
          return;
        }
        await signals.assign(id, {
          assigned_to_user_id: Number(formData.assigned_to_user_id),
          assigned_sector_id: formData.assigned_sector_id ? Number(formData.assigned_sector_id) : undefined,
        });
        toast('Signal assigned successfully', 'success');
      } else if (action === 'RESOLVED') {
        await signals.resolve(id, formData || {});
        toast('Signal resolved successfully', 'success');
        if (isOwner) setShowFeedbackSection(true);
      } else if (action === 'CANCELLED') {
        await signals.cancel(id, { reason: formData?.reason || undefined });
        toast('Signal cancelled', 'info');
      } else if (action === 'REJECTED') {
        await signals.cancel(id, { reason: formData?.reason || 'Rejected', rejection: true });
        toast('Signal rejected', 'info');
      } else if (action === 'CLOSED') {
        await signals.update(id, { status: 'CLOSED' });
        toast('Signal closed', 'success');
      } else if (action === 'SUBMITTED' && currentStatus === 'REJECTED') {
        await signals.update(id, { status: 'SUBMITTED' });
        toast('Signal reactivated', 'success');
        setShowAiSuggestion(true);
      } else if (action === 'SUBMITTED' && currentStatus === 'DRAFT') {
        await signals.update(id, { status: 'SUBMITTED' });
        toast('Signal submitted', 'success');
        setShowAiSuggestion(true);
      } else if (action === 'UNDER_REVIEW' && (currentStatus === 'ASSIGNED' || currentStatus === 'IN_PROGRESS')) {
        await signals.update(id, { status: 'UNDER_REVIEW' });
        toast('Signal returned to review', 'success');
      } else if (action === 'IN_PROGRESS') {
        await signals.process(id);
        toast('Signal is now in progress', 'success');
      } else {
        await signals.update(id, { status: action });
        toast(`Status updated to ${action}`, 'success');
      }
      onRefresh();
    } catch (err: any) {
      toast(err.response?.data?.message || 'Action failed', 'error');
    } finally {
      setLoading(false);
    }
  }, [signal.id, signal.status, isOwner, onRefresh, toast]);

  const handleFeedbackSubmit = useCallback(async () => {
    setLoading(true);
    try {
      await signals.submitFeedback(signal.id, {
        citizen_satisfaction: feedbackRating,
        citizen_feedback: feedbackText || undefined,
      });
      toast('Feedback submitted', 'success');
      setFeedbackModal(false);
      setShowFeedbackSection(false);
      onRefresh();
    } catch (err: any) {
      toast(err.response?.data?.message || 'Failed to submit feedback', 'error');
    } finally {
      setLoading(false);
    }
  }, [signal.id, feedbackRating, feedbackText, onRefresh, toast]);

  const handleAiClassify = useCallback(async () => {
    if (!signal.description) return;
    setAiClassifying(true);
    try {
      const loc = { latitude: signal.latitude, longitude: signal.longitude };
      await ai.classify({ text: signal.description, location: loc });
      toast('AI classification complete', 'success');
      setShowAiSuggestion(false);
    } catch {
      toast('AI classification failed', 'error');
    } finally {
      setAiClassifying(false);
    }
  }, [signal.description, signal.latitude, signal.longitude, toast]);

  const currentStateDef = SIGNAL_STATES[signal.status];

  return (
    <div className="max-w-sm space-y-6">
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center gap-3">
          <div className={`h-12 w-12 rounded-full flex items-center justify-center text-xl ${stateColorBg[currentStateDef?.color] || 'bg-gray-100'}`}>
            {currentStateDef?.icon || '?'}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-semibold text-gray-900">{currentStateDef?.label || signal.status}</h3>
              <span className={`h-2.5 w-2.5 rounded-full ${stateColorBadge[currentStateDef?.color] || 'bg-gray-400'}`} />
            </div>
            <p className="text-xs text-gray-500">{currentStateDef?.description || ''}</p>
          </div>
        </div>
      </div>

      <WorkflowActionPanel
        workflow={hydratedWorkflow}
        currentState={signal.status}
        userRole={userRole}
        onAction={onAction}
        loading={loading}
      />

      {showAiSuggestion && (
        <div className="bg-white rounded-lg border border-blue-200 p-6">
          <div className="flex items-start gap-3">
            <span className="text-lg">🤖</span>
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-blue-800">AI Classification Available</h4>
              <p className="text-xs text-blue-600 mt-1">Run AI classification to automatically categorize this signal.</p>
              <div className="flex gap-2 mt-3">
                <button
                  onClick={handleAiClassify}
                  disabled={aiClassifying}
                  className="px-3 py-1.5 text-xs font-medium bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {aiClassifying ? 'Classifying...' : 'Run AI Classification'}
                </button>
                <button
                  onClick={() => setShowAiSuggestion(false)}
                  className="px-3 py-1.5 text-xs font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {canFeedback && !showFeedbackSection && (
        <div className="bg-white rounded-lg border border-yellow-200 p-6">
          <div className="flex items-center gap-3 mb-3">
            <span className="text-lg">💬</span>
            <h4 className="text-sm font-semibold text-gray-900">How was your experience?</h4>
          </div>
          <p className="text-xs text-gray-500 mb-3">Your feedback helps us improve our services.</p>
          <button
            onClick={() => setFeedbackModal(true)}
            className="w-full px-4 py-2 text-sm font-medium bg-yellow-600 text-white rounded-lg hover:bg-yellow-700"
          >
            Submit Feedback
          </button>
        </div>
      )}

      {showFeedbackSection && (
        <div className="bg-white rounded-lg border border-yellow-200 p-6">
          <h4 className="text-sm font-semibold text-gray-900 mb-3">Submit Your Feedback</h4>
          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Satisfaction</label>
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setFeedbackRating(star)}
                    className={`text-xl transition-colors ${feedbackRating >= star ? 'text-yellow-400' : 'text-gray-300 hover:text-yellow-300'}`}
                  >
                    ★
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700 mb-1">Feedback (optional)</label>
              <textarea
                value={feedbackText}
                onChange={(e) => setFeedbackText(e.target.value)}
                rows={2}
                placeholder="Share your thoughts..."
                className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleFeedbackSubmit}
                disabled={loading}
                className="flex-1 px-4 py-2 text-sm font-medium bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50"
              >
                {loading ? 'Submitting...' : 'Submit'}
              </button>
              <button
                onClick={() => setShowFeedbackSection(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Skip
              </button>
            </div>
          </div>
        </div>
      )}

      <WorkflowTimeline
        workflow={hydratedWorkflow}
        entries={timelineEntries}
        currentState={signal.status}
      />

      <Modal open={feedbackModal} onClose={() => setFeedbackModal(false)} title="Submit Feedback" size="sm">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Satisfaction Rating</label>
            <div className="flex gap-2">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setFeedbackRating(star)}
                  className={`w-10 h-10 rounded-full text-lg font-bold transition-colors ${
                    feedbackRating >= star ? 'bg-yellow-400 text-white' : 'bg-gray-100 text-gray-400'
                  }`}
                >
                  {star}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Feedback (optional)</label>
            <textarea
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              rows={3}
              placeholder="Tell us about your experience..."
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button
              onClick={() => setFeedbackModal(false)}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleFeedbackSubmit}
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-white bg-yellow-600 rounded-lg hover:bg-yellow-700 disabled:opacity-50"
            >
              {loading ? 'Submitting...' : 'Submit'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
