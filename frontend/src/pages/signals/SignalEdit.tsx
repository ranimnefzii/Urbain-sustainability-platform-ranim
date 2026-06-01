import { useState, useEffect, type FormEvent } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { signals, priorities } from "../../api/endpoints";
import { useCategories } from "../../hooks/useCategories";
import LoadingSpinner from "../../components/ui/LoadingSpinner";
import type { Priority } from "../../types";

export default function SignalEdit() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { categories: catList } = useCategories();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [priorityList, setPriorityList] = useState<Priority[]>([]);
  const [form, setForm] = useState({
    title: "",
    description: "",
    category_id: "",
    priority_id: "",
    address: "",
    city: "",
    country: "",
    postal_code: "",
    is_public: true,
    is_anonymous: false,
    allow_contact: true,
    latitude: "",
    longitude: "",
    estimated_damage_cost: "",
    affected_people_count: "",
    affected_area_sqm: "",
    safety_risk_level: "",
    location_accuracy: "",
    location_description: "",
  });

  useEffect(() => {
    priorities.list().then((res) => setPriorityList(res.data.data ?? [])).catch(() => {});
  }, []);

  useEffect(() => {
    signals.get(Number(id))
      .then((res) => {
        const s = res.data.data!;
        setForm({
          title: s.title,
          description: s.description || "",
          category_id: String(s.category_id || s.category?.id || ""),
          priority_id: String(s.priority?.id || s.priority_id || ""),
          address: s.address || "",
          city: s.city || "",
          country: s.country || "",
          postal_code: s.postal_code || "",
          is_public: s.is_public,
          is_anonymous: s.is_anonymous,
          allow_contact: s.allow_contact,
          latitude: s.latitude ? String(s.latitude) : "",
          longitude: s.longitude ? String(s.longitude) : "",
          estimated_damage_cost: s.estimated_damage_cost ? String(s.estimated_damage_cost) : "",
          affected_people_count: s.affected_people_count ? String(s.affected_people_count) : "",
          affected_area_sqm: s.affected_area_sqm ? String(s.affected_area_sqm) : "",
          safety_risk_level: s.safety_risk_level ? String(s.safety_risk_level) : "",
          location_accuracy: s.location_accuracy || "",
          location_description: s.location_description || "",
        });
      })
      .catch(() => navigate("/signals"))
      .finally(() => setLoading(false));
  }, [id, navigate]);

  const update = (field: string) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const value = e.target.type === "checkbox" ? (e.target as HTMLInputElement).checked : e.target.value;
    setForm((f) => ({ ...f, [field]: value }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      const location: Record<string, any> = {};
      if (form.latitude) location.latitude = Number(form.latitude);
      if (form.longitude) location.longitude = Number(form.longitude);
      if (form.address) location.address = form.address;
      if (form.city) location.city = form.city;
      if (form.country) location.country = form.country;
      if (form.postal_code) location.postal_code = form.postal_code;

      const payload: Record<string, any> = {
        title: form.title,
        description: form.description || undefined,
        category_id: form.category_id ? Number(form.category_id) : undefined,
        location: Object.keys(location).length > 0 ? location : undefined,
        is_public: form.is_public,
        is_anonymous: form.is_anonymous,
        allow_contact: form.allow_contact,
      };

      if (form.priority_id) payload.priority_id = Number(form.priority_id);
      if (form.estimated_damage_cost) payload.estimated_damage_cost = Number(form.estimated_damage_cost);
      if (form.affected_people_count) payload.affected_people_count = Number(form.affected_people_count);
      if (form.affected_area_sqm) payload.affected_area_sqm = Number(form.affected_area_sqm);
      if (form.safety_risk_level) payload.safety_risk_level = Number(form.safety_risk_level);
      if (form.location_accuracy) payload.location_accuracy = form.location_accuracy;
      if (form.location_description) payload.location_description = form.location_description;

      await signals.update(Number(id), payload);
      navigate(`/signals/${id}`);
    } catch (err: any) {
      setError(err.response?.data?.message || "Failed to update signal");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <LoadingSpinner size="lg" className="py-20" />;

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Edit Signal</h1>
      <form onSubmit={handleSubmit} className="bg-white rounded-lg border border-gray-200 p-6 space-y-5">
        {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded text-sm">{error}</div>}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
          <input type="text" value={form.title} onChange={update("title")} required
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea value={form.description} onChange={update("description")} rows={5}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
            <select value={form.category_id} onChange={update("category_id")}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
              <option value="">No category</option>
              {catList.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
            <select value={form.priority_id} onChange={update("priority_id")}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
              <option value="">AI Auto-Assign</option>
              {priorityList.filter((p) => p.is_active).map((p) => (
                <option key={p.id} value={p.id}>{p.name} (Level {p.priority_level})</option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div className="col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
            <input type="text" value={form.address} onChange={update("address")}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
            <input type="text" value={form.country} onChange={update("country")}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
            <input type="text" value={form.city} onChange={update("city")}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Postal Code</label>
            <input type="text" value={form.postal_code} onChange={update("postal_code")}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Latitude</label>
            <input type="number" step="any" value={form.latitude} onChange={update("latitude")}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="e.g. 48.8566" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Longitude</label>
            <input type="number" step="any" value={form.longitude} onChange={update("longitude")}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" placeholder="e.g. 2.3522" />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Damage Cost ($)</label>
            <input type="number" value={form.estimated_damage_cost} onChange={update("estimated_damage_cost")} min={0}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">People Affected</label>
            <input type="number" value={form.affected_people_count} onChange={update("affected_people_count")} min={0}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Area (sqm)</label>
            <input type="number" value={form.affected_area_sqm} onChange={update("affected_area_sqm")} min={0} step="0.1"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Safety Risk (1-5)</label>
            <select value={form.safety_risk_level} onChange={update("safety_risk_level")}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
              <option value="">Not specified</option>
              {[1, 2, 3, 4, 5].map((n) => <option key={n} value={n}>{n}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Accuracy</label>
            <select value={form.location_accuracy} onChange={update("location_accuracy")}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
              <option value="">Not specified</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>
        <div className="space-y-3 pt-2 border-t border-gray-100">
          <label className="flex items-center gap-3">
            <input type="checkbox" checked={form.is_public} onChange={update("is_public")} className="rounded border-gray-300" />
            <span className="text-sm text-gray-700">Public</span>
          </label>
          <label className="flex items-center gap-3">
            <input type="checkbox" checked={form.is_anonymous} onChange={update("is_anonymous")} className="rounded border-gray-300" />
            <span className="text-sm text-gray-700">Anonymous</span>
          </label>
          <label className="flex items-center gap-3">
            <input type="checkbox" checked={form.allow_contact} onChange={update("allow_contact")} className="rounded border-gray-300" />
            <span className="text-sm text-gray-700">Allow contact</span>
          </label>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <button type="button" onClick={() => navigate(`/signals/${id}`)} className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">Cancel</button>
          <button type="submit" disabled={saving} className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium disabled:opacity-50">
            {saving ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </form>
    </div>
  );
}
