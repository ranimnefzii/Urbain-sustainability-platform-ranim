import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { signals, priorities } from "../../api/endpoints";
import { useCategories } from "../../hooks/useCategories";
import { useToast } from "../../contexts/ToastContext";
import type { Priority } from "../../types";

const LOCATION_ACCURACY_OPTIONS = ["high", "medium", "low"];

type MediaType = "image" | "video" | "document" | "audio";

interface MediaFile {
  file: File;
  type: MediaType;
  preview: string;
}

const ACCEPTED_TYPES: Record<MediaType, string> = {
  image: "image/*",
  video: "video/*",
  document: ".pdf,.doc,.docx,.xls,.xlsx,.txt",
  audio: "audio/*",
};

const MAX_FILES = 10;

export default function SignalCreate() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { categories, loading: catLoading } = useCategories();
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [priorityList, setPriorityList] = useState<Priority[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [mediaType, setMediaType] = useState<MediaType>("image");

  const [form, setForm] = useState({
    title: "",
    description: "",
    category_id: "",
    priority_id: "",
    latitude: "",
    longitude: "",
    address: "",
    city: "",
    country: "",
    postal_code: "",
    location_accuracy: "",
    location_description: "",
    is_anonymous: false,
    is_public: true,
    allow_contact: true,
    estimated_damage_cost: "",
    affected_people_count: "",
    affected_area_sqm: "",
    safety_risk_level: "",
  });

  const [mediaFiles, setMediaFiles] = useState<MediaFile[]>([]);

  useEffect(() => {
    priorities.list().then((res) => {
      setPriorityList(res.data.data ?? []);
    }).catch(() => {});
  }, []);

  useEffect(() => {
    return () => { mediaFiles.forEach((m) => URL.revokeObjectURL(m.preview)); };
  }, [mediaFiles]);

  const addFiles = (files: FileList | null, type: MediaType) => {
    if (!files) return;
    const remaining = MAX_FILES - mediaFiles.length;
    const toAdd = Array.from(files).slice(0, remaining);
    const newFiles = toAdd.map((file) => ({
      file,
      type,
      preview: URL.createObjectURL(file),
    }));
    setMediaFiles((prev) => [...prev, ...newFiles]);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) addFiles(e.target.files, mediaType);
    if (e.target) e.target.value = "";
  };

  const removeFile = (index: number) => {
    URL.revokeObjectURL(mediaFiles[index].preview);
    setMediaFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const getLocation = () => {
    if (!navigator.geolocation) { toast("Geolocation not supported", "error"); return; }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setForm((p) => ({ ...p, latitude: pos.coords.latitude.toFixed(6), longitude: pos.coords.longitude.toFixed(6) }));
        toast("Location captured", "success");
      },
      () => toast("Could not get location", "error"),
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  const validate = () => {
    const errs: Record<string, string> = {};
    if (!form.title.trim()) errs.title = "Title is required";
    if (!form.description.trim()) errs.description = "Description is required";
    if (!form.category_id) errs.category_id = "Category is required";
    if (!form.latitude) errs.latitude = "Latitude is required";
    if (!form.longitude) errs.longitude = "Longitude is required";
    const lat = parseFloat(form.latitude);
    const lng = parseFloat(form.longitude);
    if (form.latitude && (isNaN(lat) || lat < -90 || lat > 90)) errs.latitude = "Invalid latitude (-90 to 90)";
    if (form.longitude && (isNaN(lng) || lng < -180 || lng > 180)) errs.longitude = "Invalid longitude (-180 to 180)";
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const submitSignal = async (status: string) => {
    if (!validate()) return;
    setLoading(true);

    try {
      const payload: Record<string, any> = {
        title: form.title,
        description: form.description,
        category_id: Number(form.category_id),
        status,
        location: {
          latitude: parseFloat(form.latitude),
          longitude: parseFloat(form.longitude),
          address: form.address || undefined,
          city: form.city || undefined,
          country: form.country || undefined,
          postal_code: form.postal_code || undefined,
        },
        is_anonymous: form.is_anonymous,
        is_public: form.is_public,
        allow_contact: form.allow_contact,
      };

      if (form.priority_id) payload.priority_id = Number(form.priority_id);
      if (form.estimated_damage_cost) payload.estimated_damage_cost = Number(form.estimated_damage_cost);
      if (form.affected_people_count) payload.affected_people_count = Number(form.affected_people_count);
      if (form.affected_area_sqm) payload.affected_area_sqm = Number(form.affected_area_sqm);
      if (form.safety_risk_level) payload.safety_risk_level = Number(form.safety_risk_level);
      if (form.location_accuracy) payload.location_accuracy = form.location_accuracy;
      if (form.location_description) payload.location_description = form.location_description;

      const res = await signals.create(payload);
      const signalId = res.data.data!.id;

      if (mediaFiles.length > 0) {
        const formData = new FormData();
        mediaFiles.forEach((mf) => formData.append("files", mf.file));
        await signals.addMedia(signalId, formData);
      }

      toast(status === "DRAFT" ? "Draft saved" : "Signal created successfully", "success");
      navigate(`/signals/${signalId}`);
    } catch (err: any) {
      const serverErrors = err.response?.data?.errors;
      if (serverErrors) setErrors(serverErrors);
      toast(err.response?.data?.message || "Failed to create signal", "error");
    } finally {
      setLoading(false);
    }
  };

  const inputClass = (field: string) =>
    `w-full border ${errors[field] ? "border-red-400" : "border-gray-300"} rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500`;

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Submit a New Signal</h1>
      <form onSubmit={(e) => { e.preventDefault(); submitSignal("SUBMITTED"); }} className="bg-white rounded-lg border border-gray-200 p-6 space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
          <input value={form.title} onChange={(e) => setForm((p) => ({ ...p, title: e.target.value }))} className={inputClass("title")} />
          {errors.title && <p className="text-xs text-red-500 mt-1">{errors.title}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Description *</label>
          <textarea value={form.description} onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))} rows={4} className={inputClass("description")} />
          {errors.description && <p className="text-xs text-red-500 mt-1">{errors.description}</p>}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Category *</label>
            {catLoading ? (
              <div className="h-10 bg-gray-100 animate-pulse rounded-lg" />
            ) : (
              <select value={form.category_id} onChange={(e) => setForm((p) => ({ ...p, category_id: e.target.value }))} className={inputClass("category_id")}>
                <option value="">Select a category</option>
                {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            )}
            {errors.category_id && <p className="text-xs text-red-500 mt-1">{errors.category_id}</p>}
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Priority (optional)</label>
            <select value={form.priority_id} onChange={(e) => setForm((p) => ({ ...p, priority_id: e.target.value }))} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
              <option value="">AI Auto-Assign</option>
              {priorityList.filter((p) => p.is_active).map((p) => (
                <option key={p.id} value={p.id}>{p.name} (Level {p.priority_level})</option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Location *</label>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <input placeholder="Latitude" value={form.latitude} onChange={(e) => setForm((p) => ({ ...p, latitude: e.target.value }))} className={inputClass("latitude")} />
              {errors.latitude && <p className="text-xs text-red-500 mt-1">{errors.latitude}</p>}
            </div>
            <div>
              <input placeholder="Longitude" value={form.longitude} onChange={(e) => setForm((p) => ({ ...p, longitude: e.target.value }))} className={inputClass("longitude")} />
              {errors.longitude && <p className="text-xs text-red-500 mt-1">{errors.longitude}</p>}
            </div>
          </div>
          <button type="button" onClick={getLocation} className="mt-2 text-sm text-blue-600 hover:underline font-medium">Use my location</button>
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
            <input value={form.address} onChange={(e) => setForm((p) => ({ ...p, address: e.target.value }))} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
            <input value={form.city} onChange={(e) => setForm((p) => ({ ...p, city: e.target.value }))} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Country</label>
            <input value={form.country} onChange={(e) => setForm((p) => ({ ...p, country: e.target.value }))} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Postal Code</label>
            <input value={form.postal_code} onChange={(e) => setForm((p) => ({ ...p, postal_code: e.target.value }))} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Location Accuracy</label>
            <select value={form.location_accuracy} onChange={(e) => setForm((p) => ({ ...p, location_accuracy: e.target.value }))} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
              <option value="">Not specified</option>
              {LOCATION_ACCURACY_OPTIONS.map((o) => <option key={o} value={o}>{o}</option>)}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Location Description</label>
          <input value={form.location_description} onChange={(e) => setForm((p) => ({ ...p, location_description: e.target.value }))} placeholder="e.g. Near the main entrance, third floor" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
        </div>

        {/* Impact fields */}
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Est. Damage Cost ($)</label>
            <input type="number" value={form.estimated_damage_cost} onChange={(e) => setForm((p) => ({ ...p, estimated_damage_cost: e.target.value }))} min={0} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">People Affected</label>
            <input type="number" value={form.affected_people_count} onChange={(e) => setForm((p) => ({ ...p, affected_people_count: e.target.value }))} min={0} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Area (sqm)</label>
            <input type="number" value={form.affected_area_sqm} onChange={(e) => setForm((p) => ({ ...p, affected_area_sqm: e.target.value }))} min={0} step="0.1" className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm" />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Safety Risk Level (1-5)</label>
          <select value={form.safety_risk_level} onChange={(e) => setForm((p) => ({ ...p, safety_risk_level: e.target.value }))} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm">
            <option value="">Not specified</option>
            {[1, 2, 3, 4, 5].map((n) => <option key={n} value={n}>{n} - {n === 1 ? "Minimal" : n === 2 ? "Low" : n === 3 ? "Moderate" : n === 4 ? "High" : "Critical"}</option>)}
          </select>
        </div>

        {/* Media upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Media (max {MAX_FILES} files)</label>
          {mediaFiles.length > 0 && (
            <div className="flex flex-wrap gap-3 mb-3">
              {mediaFiles.map((mf, i) => (
                <div key={i} className="relative group">
                  {mf.type === "image" ? (
                    <img src={mf.preview} alt={`Upload ${i + 1}`} className="h-20 w-20 object-cover rounded-lg border" />
                  ) : mf.type === "video" ? (
                    <video src={mf.preview} className="h-20 w-20 object-cover rounded-lg border" />
                  ) : (
                    <div className="h-20 w-20 flex items-center justify-center rounded-lg border bg-gray-50 text-xs text-gray-500 text-center px-1">
                      {mf.file.name}
                    </div>
                  )}
                  <button type="button" onClick={() => removeFile(i)}
                    className="absolute -top-2 -right-2 h-5 w-5 bg-red-500 text-white rounded-full text-xs opacity-0 group-hover:opacity-100 transition">&times;</button>
                </div>
              ))}
            </div>
          )}
          {mediaFiles.length < MAX_FILES && (
            <div className="flex gap-2 items-center">
              <select value={mediaType} onChange={(e) => setMediaType(e.target.value as MediaType)}
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm">
                <option value="image">Images</option>
                <option value="video">Video</option>
                <option value="document">Document</option>
                <option value="audio">Audio</option>
              </select>
              <input ref={fileInputRef} type="file" accept={ACCEPTED_TYPES[mediaType]} multiple hidden onChange={handleFileSelect} />
              <button type="button" onClick={() => fileInputRef.current?.click()}
                className="px-4 py-2 border-2 border-dashed border-gray-300 rounded-lg text-sm text-gray-500 hover:border-blue-400 hover:text-blue-600 transition">
                + Add ({mediaFiles.length}/{MAX_FILES})
              </button>
            </div>
          )}
        </div>

        <div className="flex items-center gap-6">
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={form.is_anonymous} onChange={(e) => setForm((p) => ({ ...p, is_anonymous: e.target.checked }))} className="rounded border-gray-300" />
            Report anonymously
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={form.is_public} onChange={(e) => setForm((p) => ({ ...p, is_public: e.target.checked }))} className="rounded border-gray-300" />
            Publicly visible
          </label>
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <button type="button" onClick={() => navigate("/signals")} className="px-4 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50">Cancel</button>
          <button type="button" onClick={() => submitSignal("DRAFT")} disabled={loading}
            className="px-4 py-2 text-sm border border-gray-400 rounded-lg hover:bg-gray-50 disabled:opacity-50">
            {loading ? "Saving..." : "Save as Draft"}
          </button>
          <button type="submit" disabled={loading} className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm disabled:opacity-50">
            {loading ? "Submitting..." : "Submit Signal"}
          </button>
        </div>
      </form>
    </div>
  );
}
