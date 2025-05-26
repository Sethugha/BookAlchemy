const carousel = document.getElementById('carousel');
let rotationY = 0;

document.addEventListener('mousemove', (e) => {
  console.log("mouse location:", e.clientX, e.clientY);
  const halfWidth = window.innerWidth / 2;
  const delta = (e.clientX - halfWidth) / halfWidth;
  rotationY = delta * 24; // Maximal ±30° Drehung
  carousel.style.transform = `rotateY(${rotationY}deg) rotateX(0deg)`;
});
