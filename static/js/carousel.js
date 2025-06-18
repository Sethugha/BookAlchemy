
let angle = 0;
let velocity = 0;
let lastX = 0;
let dragging = false;
let animationFrame;
const radius = 500;
let rotateInterval = null;
var canUpdate = true;


const carousel = document.getElementById("carousel");
const details = document.getElementById("details");
const leftBtn = document.getElementById("rotate-left");
const rightBtn = document.getElementById("rotate-right");
const portrait = document.getElementById("portrait");

function noUpdate() {
        canUpdate = false;
        console.log(canUpdate);
        }

function enUpdate() {
        canUpdate = true;
        console.log(canUpdate);
        }

function toggleUpdate() {
        canUpdate = !canUpdate;
        console.log(canUpdate);
}

        document.addEventListener('DOMContentLoaded',
                                      function () {

            // Select the  element
            var area = document.getElementById('details');

            // Attach event listener for the 'mouseover' event
            area.addEventListener('mouseover', noUpdate);
            area.addEventListener('mouseout', enUpdate);

        });


function rotateCarousel(direction) {
    angle += direction * .5; // speed: 1 deg per tick
    carousel.style.transform = `rotateY(${angle}deg)`;
  }

  function startRotation(direction) {
    stopRotation(); // in case one is already running
    rotateInterval = setInterval(() => rotateCarousel(direction), 12); // ~60 FPS

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
  //console.log(books);
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
  book.title = book.title;
  bookId.value = book.isbn;
  document.getElementById('edit_title').value = book.title;
  document.getElementById('edit_author').value = book.author;
  document.getElementById('edit_isbn').value = book.isbn;
  document.getElementById('edit_year').value = book.publication_year;
  document.getElementById('edit_name').value = book.author;
  document.getElementById('edit_birth').value = book.authors_birth_date;
  if (book.authors_date_of_death != "..") {document.getElementById('edit_death').value = book.authors_date_of_death;}
  portrait.innerHTML = `<img src="${book.face}" alt="${book.author}" width="200px" height="auto" >`;
}


function render() {
  carousel.style.transform = `rotateY(${angle}deg)`;
  if (canUpdate == true) {updateDetails();}
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


  carousel.addEventListener("mousemove", e => {
    if (!dragging) return;
    const dx = e.clientX - lastX;
    angle += dx * .5;
    velocity = dx * 1;
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
    const urlPart = window.location.href;
    if (urlPart.includes("sort=title")) {books.sort((a, b) => a.title.localeCompare(b.title));
    } else if (urlPart.includes("sort=author")) {books.sort((a, b) => a.title.localeCompare(b.title));
    } else if (urlPart.includes("sort=publication_year")) {books.sort((a, b) => a.publication_year - b.publication_year);}
    if (urlPart.includes("desc=on")) {books.reverse();}
    placeBooks();
    setupInteraction();
    animate();
  });
