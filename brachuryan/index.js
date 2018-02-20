const puppeteer =require('puppeteer');

if (process.argv.length < 7) {
  console.log('Missing arguments');
  process.exit(1);
}


const FACEBOOK = 'https://www.facebook.com/search/pages/';
const QUERY = '?q=';
const FILTER_CATEGORY = '&filters_category=';

function buildQuery(keyWord, filterName, filterArgs) {
  return FACEBOOK
    + QUERY + keyWord
    + FILTER_CATEGORY + '{"name"%3a"' + filterName
    + '"%2c"args"%3a"' + filterArgs + '"}';
};

(async () => {
  const browser = await puppeteer.launch({
    headless: false,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  let url = buildQuery(process.argv[3], process.argv[5], process.argv[7]);
  await page.goto(url);
  await page.screenshot({path: '/tmp/example.png'});


  //  await browser.close();
})();
