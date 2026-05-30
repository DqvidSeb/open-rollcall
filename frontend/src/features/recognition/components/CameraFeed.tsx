// CameraFeed — stub, to be implemented
'use client';

interface CameraFeedProps {
  onFrame?: (blob: Blob) => void;
}

export function CameraFeed(_props: CameraFeedProps) {
  // TODO: render <video> element, wire useCamera, overlay canvas for bounding boxes
  return (
    <div className="relative bg-black rounded-xl overflow-hidden aspect-video">
      {/* TODO: <video> + <canvas> overlay */}
    </div>
  );
}
