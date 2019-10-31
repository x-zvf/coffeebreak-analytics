const puppeteer = require("puppeteer");
const exec = require("child_process").execFileSync;
const csv = require("csv-parser");
const fs = require("fs");

const listURL = "https://socialblade.com/youtube/top/5000/mostsubscribed";

const cfdetectstr =
  'h1><span data-translate="checking_browser">Checking your browser before accessing</span>';
//const sbdetectselector = "#top-menu-wrap";
const sbdetectselector = ".TableMonthlyStats";

let print = str => process.stdout.write(str);

async function scrape(browser, url) {
  print(`[${url}]->`);
  const page = await browser.newPage();
  try {
    await page.goto(url, { waitUntil: "networkidle0" });
  } catch {
    print("[!ERR!]\n");
    page.close();
    return {
      url: url,
      failedToOpen: true
    }
  }
   //Initial html
  let initHTML = await page.evaluate(() => document.body.innerHTML);

  print(initHTML.includes(cfdetectstr) ? "[C]->" : "");

  print("[L]->");
  await Promise.race([
    page.waitFor(sbdetectselector),
    new Promise(resolve => setTimeout(() => resolve(), 25000))
  ]);
  print("[H]->");
  let bodyHTML = await page.evaluate(() => document.body.innerHTML);

  print("[B]->");
  var res = exec("./bsp.py", [], { input: bodyHTML }).toString();
  var channel = JSON.parse(res);
  if (channel.id == "NONE") {
    print("[!E!]\n");
    page.close();
    return channel;
  }
  print("[V]->");
  var videos = await page.evaluate(
    async (url, chid) => {
      let res = await fetch(
        "https://socialblade.com/js/class/youtube-video-recent",
        {
          credentials: "include",
          headers: {
            accept: "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-requested-with": "XMLHttpRequest"
          },
          referrer: url,
          referrerPolicy: "no-referrer-when-downgrade",
          body: `channelid=${chid}`,
          method: "POST",
          mode: "cors"
        }
      );
      return await res.json();
    },
    url,
    channel.id
  );
  print("[P]->");
  // process videos:
  channel["last50uploads"] = [];
  videos.forEach(v => {
    channel["last50uploads"].push(v.created_at);
  });

  page.close();
  print("[D]\n");
  return channel;
}

async function run() {
  print("Initializing: ");
  const browser = await puppeteer.launch();
  readData = new Promise(function(resolve, reject) {
    var urls = [];
    var readline = require("readline");
    var rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      terminal: false
    });

    rl.on("line", function(line) {
      urls.push(line);
    }).on("close", () => resolve(urls));
  });

  let ws = fs.createWriteStream("res", { flags: "a" });

  urls = await readData;
  console.log("complete");

  for (let i = 2434; i < urls.length; i++) {
    const c = urls[i];
    print(`scraping ${i}/${urls.length}: `);
    data = await scrape(
      browser,
      "https://socialblade.com" + c.trim() + "/videos"
    );
    data["toplistindex"] = i;
    ws.write(JSON.stringify(data) + "\n");
  }

  ws.end();
} 
run();
