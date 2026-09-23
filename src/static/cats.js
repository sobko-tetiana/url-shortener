// Real Giphy sticker gifs, picked to match each state. Stickers (as opposed
// to regular gifs/photos) always render on a transparent background, so the
// container's shape doesn't matter. Hardcoded directly — no API key, no
// network call to find one, so there's nothing to expire or get banned.
const STATE_GIFS = {
  idle: "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3bXo2eGJjZDN3NHFqODBpcW5xd20xcXEzanNzeXBpNzhpODdiMmcwdiZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/iAIwyKeZlKBgIpH4TZ/giphy.gif",
  success: "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3NjE4N3hlcm4zM2N4MmFnMnRqenA5amZ0aGVhdmVqbzVqaG1qNzJ2MSZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/ntqm1Z8awliZCtnJIL/giphy.gif",
  celebration: "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExd2hndmJsdjA1aDFodXFuemFoenV3Y2ZvNnUzYTF1dDk2aGtiZmlsZyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/qh6Q0m0hhaYoQfHM6C/giphy.gif",
  invalid: "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnhmOXRicG5vejZiYzM4amRyOXN1cnZvaHp6bHc0cWx6enJtOXQ0ayZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/tR1ZZeJXR9RUDvaFVP/giphy.gif",
  empty: "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3NjE4N3hlcm4zM2N4MmFnMnRqenA5amZ0aGVhdmVqbzVqaG1qNzJ2MSZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/n2674pgq5KtUbZ6nVK/giphy.gif",
  deleted: "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbDhvMmRydmF2cmNuYmFzNWhsZzh0bmxwbnl2dHlmc29qdzNvZDExaiZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/NEmydmd0cXFdj4ZH9m/giphy.gif",
  forbidden: "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbDhvMmRydmF2cmNuYmFzNWhsZzh0bmxwbnl2dHlmc29qdzNvZDExaiZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/2cuI0vwb7w0wmDv7b0/giphy.gif",
  error: "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMnhmOXRicG5vejZiYzM4amRyOXN1cnZvaHp6bHc0cWx6enJtOXQ0ayZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/tR1ZZeJXR9RUDvaFVP/giphy.gif",
  offline: "https://media.giphy.com/media/v1.Y2lkPWVjZjA1ZTQ3M3RjNjVtdnJubmh2N3owZzZiNmRudTJheTVland6c3NoZzU1MWt6bSZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/hknkMAbb5sThFDDlBf/giphy.gif",
  list: "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExa3NuanAwb2c2cHlpem4ya3cxY3I3NXFpbTlxbnc2OGJhNTBkc3ZvdSZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/Wf9dyOrB0nGJn5FIYf/giphy.gif",
};

function setCat(state, text) {
  const messageEl = document.getElementById("message");
  if (messageEl) messageEl.textContent = text || "";

  const cat = document.getElementById("cat");
  const url = STATE_GIFS[state];

  if (!url) {
    cat.textContent = "\u{1F431}";
    return;
  }

  const img = document.createElement("img");
  img.src = url;
  img.alt = state;
  cat.replaceChildren(img);
}
