let angle = 0;
let velocity = 0;
let lastX = 0;
let dragging = false;
let animationFrame;
const radius = 300;
let rotateInterval = null;
const titlesort = document.getElementById('sw_title');
const authorsort = document.getElementById('sw_author');
const yearsort = document.getElementById('sw_year');
const sort_dir = document.getElementById('desc') && 'desc';

const carousel = document.getElementById("carousel");
const details = document.getElementById("details");
const leftBtn = document.getElementById("rotate-left");
const rightBtn = document.getElementById("rotate-right");
const portrait = document.getElementById("portrait");

function rotateCarousel(direction) {
    angle += direction * 1; // speed: 1 deg per tick
    carousel.style.transform = `rotateY(${currentAngle}deg)`;
  }

  function startRotation(direction) {
    stopRotation(); // in case one is already running
    rotateInterval = setInterval(() => rotateCarousel(direction), 16); // ~60 FPS

    // Visual cue (optional)
    if (direction === -1) {
      leftBtn.disabled = false;
      rightBtn.disabled = true;
    } else {
      leftBtn.disabled = true;
      rightBtn.disabled = false;
    }
  }

  function stopRotation() {
    clearInterval(rotateInterval);
    rotateInterval = null;
    leftBtn.disabled = false;
    rightBtn.disabled = false;
  }
// Start on mouse down
  leftBtn.addEventListener("mousedown", () => startRotation(-1));
  rightBtn.addEventListener("mousedown", () => startRotation(1));

  // Stop on mouse up anywhere
  document.addEventListener("mouseup", () => stopRotation());



function placeBooks() {
  carousel.innerHTML = "";
  const step = 360 / books.length;
  books.forEach((book, i) => {
    const div = document.createElement("div");
    div.className = "book";
    const rot = i * step;
    div.style.transform = `rotateY(${rot}deg) translateZ(${radius}px)`;
    div.innerHTML = `<img src="${book.img}" alt="${book.title}">`;
    carousel.appendChild(div);
  });
}


function updateDetails() {
  const step = 360 / books.length;
  let index = Math.round(-angle / step) % books.length;
  if (index < 0) index += books.length;
  const book = books[index];
  book.title = book.title.replace(' (', '</h3>(').replace(')',')<h3>')
  bookId.value = book.isbn;
  details.innerHTML = `<h3>${book.title}</h3><p>von ${book.author},
  published ${book.publication_year}<br>
  ISBN ${book.isbn}<br><br></p>`;
  portrait.innerHTML = `<img src="${book.face}" alt="${book.author}">`;

  ;

}

function render() {
  carousel.style.transform = `rotateY(${angle}deg)`;
  updateDetails();
}



function animate() {
  if (!dragging) {
    angle += velocity;
    velocity *= 0.95;
    if (Math.abs(velocity) < 0.01) velocity = 0;
  }
  render();
  animationFrame = requestAnimationFrame(animate);
}

function setupInteraction() {
  carousel.addEventListener("mousedown", e => {
    dragging = true;
    lastX = e.clientX;
    velocity = 0;
  });

  window.addEventListener("mousemove", e => {
    if (!dragging) return;
    const dx = e.clientX - lastX;
    angle += dx * 0.5;
    velocity = dx * 0.5;
    lastX = e.clientX;
    render();
  });

  window.addEventListener("mouseup", () => {
    dragging = false;
  });

  window.addEventListener("click", () => {
    if (!dragging) velocity = 0;
  });
}

fetch('/api/books')
  .then(res => res.json())
  .then(data => {
    books = data;
    if (titlesort) {books.sort((a, b) => a.title.localeCompare(b.title))};
    if (titlesort && sort_dir) {books.sort((a, b) => b.title.localeCompare(a.title))}
    if (authorsort) {books.sort((a, b) => a.author.localeCompare(b.author));}
    if (authorsort && sort_dir) {books.sort((a, b) => b.author.localeCompare(a.author));}
    if (yearsort) {books.sort((a, b) => a.publication_year - b.publication_year);}
    if (yearsort && sort_dir) {books.sort((a, b) => b.publication_year - a.publication_year);}
    placeBooks();
    setupInteraction();
    animate();
  });
