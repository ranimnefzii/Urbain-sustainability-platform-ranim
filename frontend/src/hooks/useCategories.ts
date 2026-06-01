import { useState, useEffect } from "react";
import { categories } from "../api/endpoints";
import type { Category, CategoryTree } from "../types";

export function useCategories() {
  const [cats, setCats] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    categories.list()
      .then((res) => setCats(res.data.data ?? []))
      .finally(() => setLoading(false));
  }, []);

  return { categories: cats, loading };
}

export function useCategoryTree() {
  const [tree, setTree] = useState<CategoryTree[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    categories.tree()
      .then((res) => setTree(res.data.data ?? []))
      .finally(() => setLoading(false));
  }, []);

  return { tree, loading };
}
