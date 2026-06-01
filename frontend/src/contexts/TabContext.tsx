import { createContext, useContext, useState, useCallback, type ReactNode } from "react";

export interface Tab {
  id: string;
  label: string;
  icon?: string;
  params?: Record<string, string>;
}

interface TabContextValue {
  tabs: Tab[];
  activeTab: string | null;
  openTab: (tab: Tab) => void;
  closeTab: (id: string) => void;
  setActiveTab: (id: string) => void;
  closeAll: () => void;
}

const TabContext = createContext<TabContextValue | null>(null);

export function TabProvider({ children }: { children: ReactNode }) {
  const [tabs, setTabs] = useState<Tab[]>([]);
  const [activeTab, setActiveTab] = useState<string | null>(null);

  const openTab = useCallback((tab: Tab) => {
    setTabs((prev) => {
      const exists = prev.find((t) => t.id === tab.id);
      if (exists) return prev;
      return [...prev, tab];
    });
    setActiveTab(tab.id);
  }, []);

  const closeTab = useCallback((id: string) => {
    setTabs((prev) => {
      const idx = prev.findIndex((t) => t.id === id);
      const next = prev.filter((t) => t.id !== id);
      if (activeTab === id && next.length > 0) {
        const newIdx = Math.min(idx, next.length - 1);
        setActiveTab(next[newIdx].id);
      } else if (next.length === 0) {
        setActiveTab(null);
      }
      return next;
    });
  }, [activeTab]);

  const closeAll = useCallback(() => {
    setTabs([]);
    setActiveTab(null);
  }, []);

  return (
    <TabContext.Provider value={{ tabs, activeTab, openTab, closeTab, setActiveTab, closeAll }}>
      {children}
    </TabContext.Provider>
  );
}

export function useTabs() {
  const ctx = useContext(TabContext);
  if (!ctx) throw new Error("useTabs must be used within TabProvider");
  return ctx;
}
