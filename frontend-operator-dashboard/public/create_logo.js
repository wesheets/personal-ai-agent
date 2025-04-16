// Create a simple Promethios logo placeholder
const canvas = document.createElement('canvas');
canvas.width = 300;
canvas.height = 300;
const ctx = canvas.getContext('2d');

// Draw a black background
ctx.fillStyle = '#000000';
ctx.fillRect(0, 0, canvas.width, canvas.height);

// Draw a flame-like shape
ctx.fillStyle = '#FF4500';
ctx.beginPath();
ctx.moveTo(150, 50);
ctx.bezierCurveTo(100, 150, 120, 200, 150, 250);
ctx.bezierCurveTo(180, 200, 200, 150, 150, 50);
ctx.fill();

// Add text
ctx.fillStyle = '#FFFFFF';
ctx.font = 'bold 24px Arial';
ctx.textAlign = 'center';
ctx.fillText('PROMETHIOS', 150, 280);

// Convert to blob and save
canvas.toBlob(function (blob) {
  const a = document.createElement('a');
  a.download = 'promethioslogo.png';
  a.href = URL.createObjectURL(blob);
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}, 'image/png');
