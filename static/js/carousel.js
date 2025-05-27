let angle = 0;
let velocity = 0;
let lastX = 0;
let dragging = false;
let animationFrame;
const radius = 300;


const carousel = document.getElementById("carousel");
const details = document.getElementById("details");
const deletion = document.getElementById("deletion");
const bookId = document.getElementById("bookId");


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
  ISBN ${book.isbn}<br><br></p>`
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
    placeBooks();
    setupInteraction();
    animate();
  });
