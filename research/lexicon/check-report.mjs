// SPDX-FileCopyrightText: 2026 textmode-atlas contributors
// SPDX-License-Identifier: Apache-2.0
import { chromium } from '../../apps/museum/node_modules/playwright/index.mjs';
import { writeFile } from 'node:fs/promises';
const root=process.argv[2] || new URL('../../datasets/build/lexicon/1', import.meta.url).pathname;
const browser=await chromium.launch({headless:true,args:['--no-sandbox']});
const errors=[],requests=[];
try {
 const page=await browser.newPage({viewport:{width:1440,height:1000}});
 page.on('pageerror',e=>errors.push(e.message));
 await page.route(/^https?:/,r=>{requests.push(r.request().url());return r.abort();});
 await page.goto('file://'+root+'/output/report.html');
 await page.waitForSelector('#terms tr');
 const assert=(ok,msg)=>{if(!ok)throw new Error(msg);};
 const data=await page.evaluate(()=>JSON.parse(document.getElementById('data').textContent));
 const fmt=n=>n.toLocaleString('fr-FR');
 assert(await page.locator('#stats .stat').count()===4,'Missing summary statistics');
 await page.locator('#termSearch').fill('sysop');
 assert(await page.locator('#terms').getByRole('button',{name:'sysop',exact:true}).count()===1,'Exact sysop entry absent from substring search');
 await page.getByRole('button',{name:'sysop',exact:true}).click();
 assert(await page.locator('#wordDetail .context').count()>0,'sysop contexts absent');
 assert(await page.locator('#wordDetail').innerText().then(t=>t.includes(fmt(data.lexical.find(x=>x.term==='sysop').works))),'Unexpected sysop document frequency');
 await page.locator('#eraSelect').selectOption('1990–1993');
 assert(await page.locator('#termCount').innerText().then(t=>t.includes('dénominateur')),'Missing period denominator');
 await page.screenshot({path:root+'/output/report-desktop.png',fullPage:true});
 await page.getByRole('button',{name:'Vocabulaire dans le temps'}).click();
 assert(await page.locator('#bbsChart .chart-row').count()===data.eras.length,'Missing era bins');
 assert(await page.locator('#temps').innerText().then(t=>t.includes((100*data.totals['1990–1993'].bbs/data.totals['1990–1993'].ansi_decoded).toLocaleString('fr-FR',{maximumFractionDigits:1})+' %')),'BBS baseline changed');
 await page.screenshot({path:root+'/output/report-trends.png',fullPage:true});
 await page.getByRole('button',{name:'Auteurs et groupes'}).click();
 await page.locator('#registryKind').selectOption('groups');
 await page.locator('#creditSearch').fill('read the ini');
 assert(await page.locator('#registry').innerText().then(t=>t.includes('Valeur générique possible')),'Placeholder credit not flagged');
 await page.getByRole('button',{name:'Ce qui manque'}).click();
 assert(await page.locator('#errors').innerText().then(t=>t.includes(fmt(data.errors.find(x=>x[0]==='rip')[3]))),'RIP coverage changed');
 await page.getByRole('button',{name:'Méthode et prochaines étapes'}).click();
 await page.locator('summary').click();
 assert(await page.locator('#provenance').innerText().then(t=>t.includes(data.manifest.extractors.decoder)),'Missing extractor provenance');
 await page.setViewportSize({width:390,height:844});
 await page.getByRole('button',{name:'Lexique et contextes'}).click();
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Mobile page overflow');
 await page.screenshot({path:root+'/output/report-mobile.png',fullPage:true});
 assert(errors.length===0,'JavaScript errors: '+errors.join('; '));
 assert(requests.length===0,'Report initiated external network requests');
 await writeFile(root+'/output/browser-validation.json',JSON.stringify({passed:true,checks:['lexical search','source contexts','era filter','marker denominator','credit placeholder','RIP coverage','extractor provenance','mobile width','no network requests','no JavaScript errors'],viewports:[[1440,1000],[390,844]]},null,2));
 process.stdout.write('Report verified on desktop and mobile; no network requests or JS errors.\n');
} finally {await browser.close();}
