#!/usr/bin/env node
/*
 * Syntaxpruefung der button-card-JS-Templates in den Lovelace-YAMLs.
 *
 * custom:button-card wertet alles zwischen [[[ und ]]] zur Laufzeit als
 * JavaScript aus. Ein Syntaxfehler darin bricht nicht laut ab, sondern laesst
 * die Kachel leer oder unveraendert -- der haeufigste stille Fehler in diesem
 * Repo. Dieses Skript extrahiert jeden Block und laesst ihn von der
 * JS-Engine parsen (nur parsen, nichts ausfuehren).
 *
 * Zusaetzlich wird vor typischen Verwechslungen gewarnt, die syntaktisch
 * gueltig sind, zur Laufzeit aber ins Leere laufen -- etwa "state[...]" statt
 * "states[...]".
 *
 * Aufruf: node ci/check-js-templates.js [datei ...]
 * Ohne Argumente werden alle *.yaml im Repo-Wurzelverzeichnis geprueft.
 */

'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const REPO_ROOT = path.resolve(__dirname, '..');

// Globals, die button-card dem Template bereitstellt. Wird nur fuer die
// Verwechslungs-Warnungen unten gebraucht.
const SUSPICIOUS = [
  {
    pattern: /(?<![.\w])state\s*\[/g,
    message: "'state[' -- gemeint ist vermutlich 'states['",
  },
  {
    pattern: /(?<![.\w])hass\.states\s*\.\s*\w+\s*\.\s*state\s*\(/g,
    message: "'.state(' als Funktionsaufruf -- 'state' ist eine Eigenschaft",
  },
];

function findTemplates(source) {
  const templates = [];
  const re = /\[\[\[([\s\S]*?)\]\]\]/g;
  let match;
  while ((match = re.exec(source)) !== null) {
    templates.push({
      code: match[1],
      line: source.slice(0, match.index).split('\n').length,
    });
  }
  return templates;
}

function checkFile(file) {
  const problems = [];
  const source = fs.readFileSync(file, 'utf8');
  const name = path.basename(file);
  const templates = findTemplates(source);

  for (const tpl of templates) {
    // In eine Funktion wickeln: button-card fuehrt den Block als
    // Funktionskoerper aus, deshalb sind 'return' und 'this' dort gueltig.
    try {
      new vm.Script(`(function(){${tpl.code}\n})`, { filename: name });
    } catch (err) {
      problems.push({
        file: name,
        line: tpl.line,
        level: 'FEHLER',
        message: `JS-Template ist syntaktisch ungueltig -- ${err.message}`,
      });
      // Bei kaputter Syntax lohnt die Heuristik unten nicht mehr.
      continue;
    }

    for (const { pattern, message } of SUSPICIOUS) {
      pattern.lastIndex = 0;
      if (pattern.test(tpl.code)) {
        problems.push({
          file: name,
          line: tpl.line,
          level: 'WARNUNG',
          message,
        });
      }
    }
  }

  return { count: templates.length, problems };
}

function main(argv) {
  const files =
    argv.length > 0
      ? argv
      : fs
          .readdirSync(REPO_ROOT)
          // Nur die Kartendateien -- Konfiguration wie .pre-commit-config.yaml
          // enthaelt keine button-card-Templates.
          .filter((f) => f.endsWith('.yaml') && !f.startsWith('.'))
          .sort()
          .map((f) => path.join(REPO_ROOT, f));

  if (files.length === 0) {
    console.log('Keine YAML-Dateien gefunden.');
    return 1;
  }

  let templateCount = 0;
  let errors = 0;
  let warnings = 0;

  for (const file of files) {
    const { count, problems } = checkFile(file);
    templateCount += count;
    for (const p of problems) {
      if (p.level === 'FEHLER') errors++;
      else warnings++;
      console.log(`${p.level.padEnd(7)} ${p.file}:${p.line}: ${p.message}`);
    }
  }

  console.log(
    `\n${files.length} Datei(en), ${templateCount} JS-Template(s) geprueft, ` +
      `${errors} Fehler, ${warnings} Warnung(en).`
  );

  // Warnungen sind Heuristik und brechen den Build nicht.
  return errors > 0 ? 1 : 0;
}

process.exit(main(process.argv.slice(2)));
