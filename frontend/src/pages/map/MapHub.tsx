import HubLayout from "../../components/hub/HubLayout";
import SignalMap from "../signals/SignalMap";

export default function MapHub() {
  return (
    <div className="flex gap-6 h-full">
      <div className="flex-1 min-w-0">
        <HubLayout title="Carte Interactive" description="Explorer, analyser et gérer les signalements sur la carte">
          <SignalMap />
        </HubLayout>
      </div>
    </div>
  );
}
