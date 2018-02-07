let startCrawl = function() {
  fetch('https://sally.patito.club/start',
    {headers: new Headers({'Content-Type': 'application/json'}),
      method: 'GET', cache: 'no-store'})
    .then(res => res.json())
  .then(out => {
    console.log(out);
  });
}

async function fetchItem(endpoint, target_element, hInit) {
     fetch('https://sally.patito.club/' + endpoint, hInit)
      .then(res => res.json())
      .then((out) => {
        e = document.getElementById(target_element);
        out.forEach(function(item) {
          li = document.createElement("li");
          li.appendChild(document.createTextNode(item['name']));
          e.appendChild(li)
        });
      });
};

function initHome() {
  let hHeaders = new Headers({
      'Content-Type': 'application/json'
    });

  // Fetch items from Google drive
    let hInit = {
      headers: hHeaders,
      method: 'GET',
      mode: 'cors',
      cache: 'no-store',
    };

  fetchItem('queue','block-a', hInit);
  fetchItem('output','block-b', hInit);
  fetchItem('processing','block-c', hInit);

  // Attach event handlers
  document.getElementById('start_button').addEventListener("click",
  startCrawl)
}
