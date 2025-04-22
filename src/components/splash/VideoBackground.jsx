export default function VideoBackground() {
  return (
    <video
      autoPlay
      loop
      muted
      playsInline
      className="absolute w-full h-full object-cover z-[-1]"
      src="/assets/promethiosbackgoundvideo.mp4"
    />
  );
}
