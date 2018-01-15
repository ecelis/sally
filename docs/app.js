var JSONFormatter = require('./json-formatter.js').default;

let live = document.getElementById('live');
let hoverPreviewEnabledCheckbox = document.getElementById('hoverPreviewEnabled');

function render() {
    live.style.backgroundColor = 'transparent';
    var result = document.getElementById('live-result');
    try {
        var formatter = new JSONFormatter(JSON.parse(live.value), 1, { hoverPreviewEnabled: hoverPreviewEnabledCheckbox.checked });
        result.innerHTML = '';
        result.appendChild(formatter.render());
    } catch (e) {
        live.style.backgroundColor = 'rgba(255, 87, 34, 0.35)';
    }
}
live.addEventListener('keyup', render);

render();
