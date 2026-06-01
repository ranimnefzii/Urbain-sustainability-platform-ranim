import { useState } from 'react';
import type { WorkflowDefinition } from './types';

interface TimelineEntry {
  stateId: string;
  timestamp?: string;
  note?: string;
}

interface WorkflowTimelineProps {
  workflow: WorkflowDefinition;
  entries: TimelineEntry[];
  currentState: string;
}

const colorMap: Record<string, string> = {
  gray: 'bg-gray-400',
  yellow: 'bg-yellow-400',
  blue: 'bg-blue-500',
  indigo: 'bg-indigo-500',
  purple: 'bg-purple-500',
  green: 'bg-green-500',
  red: 'bg-red-500',
};

const ringMap: Record<string, string> = {
  gray: 'ring-gray-300',
  yellow: 'ring-yellow-300',
  blue: 'ring-blue-300',
  indigo: 'ring-indigo-300',
  purple: 'ring-purple-300',
  green: 'ring-green-300',
  red: 'ring-red-300',
};

export default function WorkflowTimeline({ workflow, entries, currentState }: WorkflowTimelineProps) {
  const [selectedEntry, setSelectedEntry] = useState<number | null>(null);
  const allStates = Object.values(workflow.states);
  const currentIndex = allStates.findIndex((s) => s.id === currentState);

  const timelineEntries: TimelineEntry[] = entries.length > 0
    ? entries
    : allStates.map((s) => ({ stateId: s.id }));

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5">
      <h3 className="text-sm font-semibold text-gray-900 mb-4">Workflow Timeline</h3>
      <div className="relative">
        {timelineEntries.map((entry, idx) => {
          const state = workflow.states[entry.stateId];
          if (!state) return null;

          const entryIndex = allStates.findIndex((s) => s.id === entry.stateId);
          const isCompleted = entryIndex < currentIndex;
          const isCurrent = entry.stateId === currentState;
          const isFuture = entryIndex > currentIndex;
          const isTerminal = workflow.terminalStates.includes(entry.stateId);

          return (
            <div key={entry.stateId + idx}>
              <div className="flex gap-3">
                <div className="flex flex-col items-center">
                  <button
                    onClick={() => setSelectedEntry(selectedEntry === idx ? null : idx)}
                    className={`relative h-8 w-8 rounded-full flex items-center justify-center text-sm flex-shrink-0 transition-all
                      ${isCurrent
                        ? `${colorMap[state.color] || 'bg-blue-500'} text-white ring-4 ${ringMap[state.color] || 'ring-blue-300'} animate-pulse`
                        : isCompleted
                        ? 'bg-green-500 text-white ring-4 ring-green-200'
                        : isTerminal
                        ? `${colorMap[state.color] || 'bg-gray-400'} text-white`
                        : 'bg-gray-200 text-gray-400'
                      }`}
                  >
                    {isCompleted ? (
                      <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" /></svg>
                    ) : isTerminal ? (
                      <span className="text-xs">{state.icon}</span>
                    ) : (
                      <span className="text-xs">{state.icon}</span>
                    )}
                  </button>
                  {idx < timelineEntries.length - 1 && (
                    <div className={`w-0.5 h-6 ${isCompleted ? 'bg-green-400' : 'bg-gray-200'}`} />
                  )}
                </div>
                <div className={`pb-6 flex-1 min-w-0 ${isFuture ? 'opacity-40' : ''}`}>
                  <button
                    onClick={() => setSelectedEntry(selectedEntry === idx ? null : idx)}
                    className="text-left w-full"
                  >
                    <div className="flex items-center gap-2">
                      <span className={`text-xs font-semibold ${isCurrent ? 'text-blue-700' : isCompleted ? 'text-green-700' : 'text-gray-500'}`}>
                        {state.label}
                      </span>
                      {isCurrent && (
                        <span className="text-[10px] font-medium text-blue-600 bg-blue-100 px-1.5 py-0.5 rounded-full">Current</span>
                      )}
                      {isTerminal && isCompleted && (
                        <span className="text-[10px] font-medium text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded-full">End</span>
                      )}
                      {entry.timestamp && (
                        <span className="text-[10px] text-gray-400">{entry.timestamp}</span>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-0.5">{state.description}</p>
                  </button>
                  {selectedEntry === idx && (
                    <div className="mt-2 p-3 bg-gray-50 border border-gray-200 rounded-lg">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-lg">{state.icon}</span>
                        <span className="text-sm font-medium text-gray-900">{state.label}</span>
                        <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded-full ${
                          state.category === 'initial' ? 'bg-gray-100 text-gray-600' :
                          state.category === 'active' ? 'bg-blue-100 text-blue-600' :
                          state.category === 'success' ? 'bg-green-100 text-green-600' :
                          state.category === 'failure' ? 'bg-red-100 text-red-600' :
                          'bg-gray-100 text-gray-600'
                        }`}>{state.category}</span>
                      </div>
                      <p className="text-xs text-gray-600">{state.description}</p>
                      {entry.note && <p className="text-xs text-gray-500 mt-1 italic">{entry.note}</p>}
                      {entry.timestamp && <p className="text-xs text-gray-400 mt-1">{entry.timestamp}</p>}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
