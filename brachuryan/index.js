const puppeteer =require('puppeteer');

if (process.argv.length < 7) {
  console.log('Missing arguments');
  process.exit(1);
}

const FACEBOOK = 'https://www.facebook.com/';
const LOGIN = 'login';
const SEARCH = 'search/pages/';
const QUERY = '?q=';
const FILTER_CATEGORY = '&filters_category=';
const LOGIN_BUTTON = 'button#loginbutton';
const USERNAME_FIELD = 'input#email';
const PASSWORD_FIELD = 'input#pass';

function login() {
  return FACEBOOK + LOGIN;
};

function buildQuery(keyWord, filterName, filterArgs) {
  return FACEBOOK + SEARCH
    + QUERY + keyWord
    + FILTER_CATEGORY + '{"name"%3a"' + filterName
    + '"%2c"args"%3a"' + filterArgs + '"}';
};

function extractItems() {
    const extractedElements = document.querySelectorAll('#boxes > div.box');
    const items = [];
    for (let element of extractedElements) {
          items.push(element.innerText);
        }
    return items;
}

async function scrapeInfiniteScrollItems(
    page,
    extractItems,
    itemTargetCount,
    scrollDelay = 1000,
) {
    let items = [];
    try {
          let previousHeight;
          while (items.length < itemTargetCount) {
                  items = await page.evaluate(extractItems);
                  previousHeight = await page.evaluate('document.body.scrollHeight');
                  await page.evaluate('window.scrollTo(0, document.body.scrollHeight)');
                  await page.waitForFunction(`document.body.scrollHeight > ${previousHeight}`);
                  await page.waitFor(scrollDelay);
                }
        } catch(e) { }
    return items;
}

(async () => {
  const browser = await puppeteer.launch({
    headless: false,
    slowMo: 1,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  let url = buildQuery(process.argv[3], process.argv[5], process.argv[7]);
  await page.goto(login(), {
    waitUntil: 'networkidle2'
  });
  await page.waitForSelector(LOGIN_BUTTON);
  await page.focus(USERNAME_FIELD);
  await page.type(USERNAME_FIELD, process.env.FB_USERNAME);
  await page.focus(PASSWORD_FIELD);
  await page.type(PASSWORD_FIELD, process.env.FB_PASSWD);
  await page.click(LOGIN_BUTTON);
  await page.goto(url);
  const items = await scrapeInfiniteScrollItems(page, extractItems, 100);
  //  fs.writeFileSync('./items.txt', items.join('\n') + '\n');
  await page.keyboard.press('Tab');
  await page.screenshot({path: '/tmp/example.png'});

  await browser.close();
})();
