import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { signals, priorities } from "../../api/endpoints";
import { useCategories } from "../../hooks/useCategories";
import { useToast } from "../../contexts/ToastContext";
import type { Priority } from "../../types";

const LOCATION_ACCURACY_OPTIONS = ["high", "medium", "low"];
type MediaType = "image" | "video" | "document" | "audio";
interface MediaFile { file: File; type: MediaType; preview: string; }
const ACCEPTED_TYPES: Record<MediaType, string> = {
  image: "image/*", video: "video/*",
  document: ".pdf,.doc,.docx,.xls,.xlsx,.txt", audio: "audio/*",
};
const MAX_FILES = 10;
const STEPS = ["Informations", "Localisation", "Impact", "Médias", "Confirmation"];

export default function SignalCreate() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { categories, loading: catLoading } = useCategories();
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [priorityList, setPriorityList] = useState<Priority[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [mediaType, setMediaType] = useState<MediaType>("image");
  const [step, setStep] = useState(0);

  const [form, setForm] = useState({
    title: "", description: "", category_id: "", priority_id: "",
    latitude: "", longitude: "", address: "", city: "", country: "",
    postal_code: "", location_accuracy: "", location_description: "",
    is_anonymous: false, is_public: true, allow_contact: true,
    estimated_damage_cost: "", affected_people_count: "",
    affected_area_sqm: "", safety_risk_level: "",
  });

  const [mediaFiles, setMediaFiles] = useState<MediaFile[]>([]);

  useEffect(() => {
    priorities.list().then((res) => setPriorityList(res.data.data ?? [])).catch(() => {});
  }, []);

  useEffect(() => {
    return () => { mediaFiles.forEach((m) => URL.revokeObjectURL(m.preview)); };
  }, [mediaFiles]);

  const addFiles = (files: FileList | null, type: MediaType) => {
    if (!files) return;
    const remaining = MAX_FILES - mediaFiles.length;
    const toAdd = Array.from(files).slice(0, remaining);
    const newFiles = toAdd.map((file) => ({ file, type, preview: URL.createObjectURL(file) }));
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
    if (!navigator.geolocation) { toast("Géolocalisation non supportée", "error"); return; }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setForm((p) => ({ ...p, latitude: pos.coords.latitude.toFixed(6), longitude: pos.coords.longitude.toFixed(6) }));
        toast("Position capturée", "success");
      },
      () => toast("Impossible d'obtenir la position", "error"),
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  const validateStep = (): boolean => {
    const errs: Record<string, string> = {};
    if (step === 0) {
      if (!form.title.trim()) errs.title = "Le titre est requis";
      if (!form.description.trim()) errs.description = "La description est requise";
      if (!form.category_id) errs.category_id = "La catégorie est requise";
    } else if (step === 1) {
      if (!form.latitude) errs.latitude = "La latitude est requise";
      if (!form.longitude) errs.longitude = "La longitude est requise";
      const lat = parseFloat(form.latitude);
      const lng = parseFloat(form.longitude);
      if (form.latitude && (isNaN(lat) || lat < -90 || lat > 90)) errs.latitude = "Latitude invalide (-90 à 90)";
      if (form.longitude && (isNaN(lng) || lng < -180 || lng > 180)) errs.longitude = "Longitude invalide (-180 à 180)";
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const nextStep = () => { if (validateStep()) setStep((s) => Math.min(s + 1, STEPS.length - 1)); };
  const prevStep = () => setStep((s) => Math.max(s - 1, 0));

  const submitSignal = async (status: string) => {
    if (!validateStep()) return;
    setLoading(true);
    try {
      const payload: Record<string, any> = {
        title: form.title, description: form.description,
        category_id: Number(form.category_id), status,
        location: { latitude: parseFloat(form.latitude), longitude: parseFloat(form.longitude),
          address: form.address || undefined, city: form.city || undefined,
          country: form.country || undefined, postal_code: form.postal_code || undefined },
        is_anonymous: form.is_anonymous, is_public: form.is_public, allow_contact: form.allow_contact,
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
      toast(status === "DRAFT" ? "Brouillon sauvegardé" : "Signalement créé avec succès", "success");
      navigate(`/signals/${signalId}`);
    } catch (err: any) {
      const serverErrors = err.response?.data?.errors;
      if (serverErrors) setErrors(serverErrors);
      toast(err.response?.data?.message || "Échec de la création", "error");
    } finally {
      setLoading(false);
    }
  };

  const renderStepIndicator = () => (
    <div className="flex items-center justify-between mb-8">
      {STEPS.map((label, i) => (
        <div key={i} className="flex items-center flex-1">
          <div className="flex items-center gap-2.5">
            <div className={`w-9 h-9 rounded-xl flex items-center justify-center text-sm font-bold transition-all duration-300 ${
              i === step ? "bg-brand-600 text-white shadow-lg shadow-brand-600/30 scale-110" :
              i < step ? "bg-green-500 text-white" : "bg-surface-100 text-surface-400"
            }`}>
              {i < step ? (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                </svg>
              ) : i + 1}
            </div>
            <span className={`text-xs font-medium hidden sm:block ${i === step ? "text-brand-600" : i < step ? "text-green-600" : "text-surface-400"}`}>
              {label}
            </span>
          </div>
          {i < STEPS.length - 1 && (
            <div className={`flex-1 h-0.5 mx-3 rounded transition-colors duration-300 ${i < step ? "bg-green-400" : "bg-surface-200"}`} />
          )}
        </div>
      ))}
    </div>
  );

  const inputClass = (field: string) =>
    `w-full px-4 py-2.5 border ${errors[field] ? "border-red-300 bg-red-50" : "border-surface-300"} rounded-xl text-sm text-surface-800 placeholder-surface-400 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500`;

  return (
    <div className="max-w-3xl mx-auto animate-fade-in">
      <div className="mb-6">
        <h1 className="page-title">Nouveau signalement</h1>
        <p className="text-sm text-surface-500 mt-1">Signalez un problème urbain en quelques étapes</p>
      </div>

      {renderStepIndicator()}

      <div className="card">
        <div className="card-body space-y-6">
          {/* Step 0: Basic Info */}
          {step === 0 && (
            <div className="space-y-5 animate-fade-in">
              <div>
                <label className="input-label">Titre du signalement *</label>
                <input value={form.title} onChange={(e) => setForm((p) => ({ ...p, title: e.target.value }))}
                  placeholder="Ex : Nid-de-poule avenue Habib Bourguiba" className={inputClass("title")} />
                {errors.title && <p className="text-xs text-red-500 mt-1.5 flex items-center gap-1"><svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" /></svg>{errors.title}</p>}
              </div>
              <div>
                <label className="input-label">Description *</label>
                <textarea value={form.description} onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))} rows={5}
                  placeholder="Décrivez le problème en détail : nature, emplacement précis, depuis quand..." className={inputClass("description")} />
                {errors.description && <p className="text-xs text-red-500 mt-1.5 flex items-center gap-1"><svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" /></svg>{errors.description}</p>}
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="input-label">Catégorie *</label>
                  {catLoading ? (
                    <div className="h-10 bg-surface-100 animate-pulse rounded-xl" />
                  ) : (
                    <select value={form.category_id} onChange={(e) => setForm((p) => ({ ...p, category_id: e.target.value }))} className={inputClass("category_id")}>
                      <option value="">Sélectionnez une catégorie</option>
                      {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                    </select>
                  )}
                  {errors.category_id && <p className="text-xs text-red-500 mt-1.5">{errors.category_id}</p>}
                </div>
                <div>
                  <label className="input-label">Priorité (optionnel)</label>
                  <select value={form.priority_id} onChange={(e) => setForm((p) => ({ ...p, priority_id: e.target.value }))} className="w-full px-4 py-2.5 border border-surface-300 rounded-xl text-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500">
                    <option value="">Attribution automatique (IA)</option>
                    {priorityList.filter((p) => p.is_active).map((p) => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Step 1: Location */}
          {step === 1 && (
            <div className="space-y-5 animate-fade-in">
              <div className="flex items-center justify-between">
                <label className="input-label mb-0">Coordonnées GPS *</label>
                <button type="button" onClick={getLocation}
                  className="btn-ghost text-brand-600 text-xs flex items-center gap-1.5">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                  Utiliser ma position
                </button>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <input placeholder="Latitude" value={form.latitude} onChange={(e) => setForm((p) => ({ ...p, latitude: e.target.value }))} className={inputClass("latitude")} />
                  {errors.latitude && <p className="text-xs text-red-500 mt-1.5">{errors.latitude}</p>}
                </div>
                <div>
                  <input placeholder="Longitude" value={form.longitude} onChange={(e) => setForm((p) => ({ ...p, longitude: e.target.value }))} className={inputClass("longitude")} />
                  {errors.longitude && <p className="text-xs text-red-500 mt-1.5">{errors.longitude}</p>}
                </div>
              </div>

              <div className="divider" />

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="input-label">Adresse</label>
                  <input value={form.address} onChange={(e) => setForm((p) => ({ ...p, address: e.target.value }))} placeholder="Rue, numéro" className={inputClass("address")} />
                </div>
                <div>
                  <label className="input-label">Ville</label>
                  <input value={form.city} onChange={(e) => setForm((p) => ({ ...p, city: e.target.value }))} placeholder="Ville" className={inputClass("city")} />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="input-label">Code postal</label>
                  <input value={form.postal_code} onChange={(e) => setForm((p) => ({ ...p, postal_code: e.target.value }))} placeholder="Code postal" className={inputClass("postal_code")} />
                </div>
                <div>
                  <label className="input-label">Pays</label>
                  <input value={form.country} onChange={(e) => setForm((p) => ({ ...p, country: e.target.value }))} placeholder="Pays" className={inputClass("country")} />
                </div>
                <div>
                  <label className="input-label">Précision</label>
                  <select value={form.location_accuracy} onChange={(e) => setForm((p) => ({ ...p, location_accuracy: e.target.value }))} className="w-full px-4 py-2.5 border border-surface-300 rounded-xl text-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500">
                    <option value="">Non spécifiée</option>
                    {LOCATION_ACCURACY_OPTIONS.map((o) => <option key={o} value={o}>{o === "high" ? "Élevée" : o === "medium" ? "Moyenne" : "Faible"}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="input-label">Description de l'emplacement</label>
                <input value={form.location_description} onChange={(e) => setForm((p) => ({ ...p, location_description: e.target.value }))} placeholder="Ex : Près de l'entrée principale, au 3ème étage" className={inputClass("location_description")} />
              </div>
            </div>
          )}

          {/* Step 2: Impact */}
          {step === 2 && (
            <div className="space-y-5 animate-fade-in">
              <div className="bg-brand-50 border border-brand-100 rounded-xl p-4 text-sm text-brand-800 flex items-start gap-3">
                <svg className="w-5 h-5 text-brand-500 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" /></svg>
                Ces informations aident à prioriser votre signalement. L'IA les utilisera pour évaluer l'urgence.
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="input-label">Coût estimé ($)</label>
                  <input type="number" value={form.estimated_damage_cost} onChange={(e) => setForm((p) => ({ ...p, estimated_damage_cost: e.target.value }))} min={0} placeholder="0" className={inputClass("estimated_damage_cost")} />
                </div>
                <div>
                  <label className="input-label">Personnes affectées</label>
                  <input type="number" value={form.affected_people_count} onChange={(e) => setForm((p) => ({ ...p, affected_people_count: e.target.value }))} min={0} placeholder="0" className={inputClass("affected_people_count")} />
                </div>
                <div>
                  <label className="input-label">Zone (m²)</label>
                  <input type="number" value={form.affected_area_sqm} onChange={(e) => setForm((p) => ({ ...p, affected_area_sqm: e.target.value }))} min={0} step="0.1" placeholder="0" className={inputClass("affected_area_sqm")} />
                </div>
              </div>
              <div>
                <label className="input-label">Niveau de risque (1-5)</label>
                <select value={form.safety_risk_level} onChange={(e) => setForm((p) => ({ ...p, safety_risk_level: e.target.value }))} className="w-full px-4 py-2.5 border border-surface-300 rounded-xl text-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500">
                  <option value="">Non spécifié</option>
                  {[1, 2, 3, 4, 5].map((n) => <option key={n} value={n}>{n} - {n === 1 ? "Minimal" : n === 2 ? "Faible" : n === 3 ? "Modéré" : n === 4 ? "Élevé" : "Critique"}</option>)}
                </select>
              </div>
            </div>
          )}

          {/* Step 3: Media */}
          {step === 3 && (
            <div className="space-y-5 animate-fade-in">
              <div>
                <label className="input-label">Photos et documents (max {MAX_FILES} fichiers)</label>
                {mediaFiles.length > 0 && (
                  <div className="flex flex-wrap gap-3 mb-3">
                    {mediaFiles.map((mf, i) => (
                      <div key={i} className="relative group">
                        {mf.type === "image" ? (
                          <img src={mf.preview} alt={`Upload ${i + 1}`} className="h-24 w-24 object-cover rounded-xl border border-surface-200" />
                        ) : mf.type === "video" ? (
                          <video src={mf.preview} className="h-24 w-24 object-cover rounded-xl border border-surface-200" />
                        ) : (
                          <div className="h-24 w-24 flex items-center justify-center rounded-xl border border-surface-200 bg-surface-50 text-xs text-surface-500 text-center px-1">
                            {mf.file.name}
                          </div>
                        )}
                        <button type="button" onClick={() => removeFile(i)}
                          className="absolute -top-2 -right-2 h-5 w-5 bg-red-500 text-white rounded-full text-xs opacity-0 group-hover:opacity-100 transition-all shadow-md hover:bg-red-600">&times;</button>
                      </div>
                    ))}
                  </div>
                )}
                {mediaFiles.length < MAX_FILES && (
                  <div className="flex gap-3 items-center">
                    <select value={mediaType} onChange={(e) => setMediaType(e.target.value as MediaType)}
                      className="border border-surface-300 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500">
                      <option value="image">Images</option>
                      <option value="video">Vidéo</option>
                      <option value="document">Document</option>
                      <option value="audio">Audio</option>
                    </select>
                    <input ref={fileInputRef} type="file" accept={ACCEPTED_TYPES[mediaType]} multiple hidden onChange={handleFileSelect} />
                    <button type="button" onClick={() => fileInputRef.current?.click()}
                      className="px-5 py-2.5 border-2 border-dashed border-surface-300 rounded-xl text-sm text-surface-500 hover:border-brand-400 hover:text-brand-600 transition-all duration-200 font-medium flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
                      Ajouter ({mediaFiles.length}/{MAX_FILES})
                    </button>
                  </div>
                )}
              </div>

              <div className="divider" />

              <div className="space-y-3">
                <label className="input-label">Options de publication</label>
                <div className="grid grid-cols-3 gap-3">
                  <label className={`flex items-center gap-3 p-3 rounded-xl border-2 cursor-pointer transition-all duration-200 ${form.is_anonymous ? "border-brand-500 bg-brand-50" : "border-surface-200 hover:border-surface-300"}`}>
                    <input type="checkbox" checked={form.is_anonymous} onChange={(e) => setForm((p) => ({ ...p, is_anonymous: e.target.checked }))} className="sr-only" />
                    <div className={`w-5 h-5 rounded-md flex items-center justify-center transition-all ${form.is_anonymous ? "bg-brand-600" : "bg-surface-100"}`}>
                      {form.is_anonymous && <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-surface-800">Anonyme</p>
                      <p className="text-xs text-surface-400">Masquer mon identité</p>
                    </div>
                  </label>
                  <label className={`flex items-center gap-3 p-3 rounded-xl border-2 cursor-pointer transition-all duration-200 ${form.is_public ? "border-brand-500 bg-brand-50" : "border-surface-200 hover:border-surface-300"}`}>
                    <input type="checkbox" checked={form.is_public} onChange={(e) => setForm((p) => ({ ...p, is_public: e.target.checked }))} className="sr-only" />
                    <div className={`w-5 h-5 rounded-md flex items-center justify-center transition-all ${form.is_public ? "bg-brand-600" : "bg-surface-100"}`}>
                      {form.is_public && <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-surface-800">Public</p>
                      <p className="text-xs text-surface-400">Visible par tous</p>
                    </div>
                  </label>
                  <label className={`flex items-center gap-3 p-3 rounded-xl border-2 cursor-pointer transition-all duration-200 ${form.allow_contact ? "border-brand-500 bg-brand-50" : "border-surface-200 hover:border-surface-300"}`}>
                    <input type="checkbox" checked={form.allow_contact} onChange={(e) => setForm((p) => ({ ...p, allow_contact: e.target.checked }))} className="sr-only" />
                    <div className={`w-5 h-5 rounded-md flex items-center justify-center transition-all ${form.allow_contact ? "bg-brand-600" : "bg-surface-100"}`}>
                      {form.allow_contact && <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" /></svg>}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-surface-800">Contact</p>
                      <p className="text-xs text-surface-400">Autoriser le contact</p>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* Step 4: Confirmation */}
          {step === 4 && (
            <div className="space-y-5 animate-fade-in">
              <div className="bg-green-50 border border-green-100 rounded-xl p-5 text-center">
                <div className="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <svg className="w-7 h-7 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                </div>
                <h3 className="text-lg font-semibold text-green-800">Vérification finale</h3>
                <p className="text-sm text-green-600 mt-1">Veuillez vérifier les informations avant de soumettre</p>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="card p-4">
                  <p className="font-semibold text-surface-700 mb-2 flex items-center gap-2">
                    <svg className="w-4 h-4 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                    Informations
                  </p>
                  <p className="text-surface-600"><span className="text-surface-400">Titre :</span> {form.title}</p>
                  <p className="text-surface-600 mt-1"><span className="text-surface-400">Description :</span> {form.description?.slice(0, 100)}...</p>
                </div>
                <div className="card p-4">
                  <p className="font-semibold text-surface-700 mb-2 flex items-center gap-2">
                    <svg className="w-4 h-4 text-brand-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" /></svg>
                    Localisation
                  </p>
                  <p className="text-surface-600"><span className="text-surface-400">Lat :</span> {form.latitude}</p>
                  <p className="text-surface-600"><span className="text-surface-400">Lng :</span> {form.longitude}</p>
                  {form.address && <p className="text-surface-600"><span className="text-surface-400">Adresse :</span> {form.address}</p>}
                </div>
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex items-center justify-between pt-4 border-t border-surface-100">
            <div>
              {step > 0 ? (
                <button type="button" onClick={prevStep} className="btn-ghost flex items-center gap-1.5">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
                  Retour
                </button>
              ) : (
                <button type="button" onClick={() => navigate("/signals")} className="btn-ghost">
                  Annuler
                </button>
              )}
            </div>
            <div className="flex gap-3">
              {step === 0 && (
                <button type="button" onClick={() => submitSignal("DRAFT")} disabled={loading}
                  className="btn-secondary text-sm">
                  {loading ? "Sauvegarde..." : "Brouillon"}
                </button>
              )}
              {step < STEPS.length - 1 ? (
                <button type="button" onClick={nextStep} className="btn-primary flex items-center gap-1.5">
                  Suivant
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" /></svg>
                </button>
              ) : (
                <div className="flex gap-3">
                  <button type="button" onClick={() => submitSignal("DRAFT")} disabled={loading}
                    className="btn-secondary">
                    {loading ? "Sauvegarde..." : "Sauvegarder brouillon"}
                  </button>
                  <button type="button" onClick={() => submitSignal("SUBMITTED")} disabled={loading}
                    className="btn-primary">
                    {loading ? (
                      <span className="flex items-center gap-2">
                        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" /><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" /></svg>
                        Envoi...
                      </span>
                    ) : "Soumettre le signalement"}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
