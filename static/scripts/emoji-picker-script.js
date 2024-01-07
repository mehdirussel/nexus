// emoji-picker-script.js
import 'emoji-picker-element';

document.addEventListener('DOMContentLoaded', function () {
  // Add the emoji picker to the HTML
  const input = document.querySelector('input'); // Change this selector based on your input element
  const picker = document.createElement('emoji-picker');
  input.after(picker);
});