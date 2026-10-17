# Home Assistant OS unter Proxmox: Festplatte vergrößern

Stand: 2026-09-02. Instanz: **HA OS 18.2** (`board: ova`, Virtualisierung `kvm`),
Core 2026.8.3, Datenträger laut Supervisor `QEMU-HARDDISK-QM00005`.
Belegung vor dem Aufräumen: **27,3 von 30,8 GB**.

## Lohnt sich das?

Ja. 32 GB ist die Standardgröße des HAOS-Images und für diese Installation zu
knapp. Was den Platz frisst:

| Posten | Größe |
|---|---|
| Recorder-Datenbank (SQLite) | ≈ 3,1 GB |
| Automatische Backups, lokal (5 Stück) | ≈ 6,5 GB |
| Alt-Backups von 2024 | ≈ 1,0 GB |
| Container-Images Core + 7 Add-ons | mehrere GB |

Dazu kommt: Jedes Core-Update lädt ein neues Image **zusätzlich** zum
laufenden und legt vorher ein Backup an. Eine fast volle Platte ist genau der
Fall, in dem ein Update abbricht oder die SQLite-Datenbank Schaden nimmt.

**Empfehlung: auf 64 GB erhöhen.** Wer Medien, Kamera-Snapshots oder mehr
lokale Backups vorhalten will, nimmt 100 GB. Bei Thin-Provisioning (LVM-thin,
ZFS, qcow2) belegt der Zuwachs auf dem Host erst dann Platz, wenn er wirklich
genutzt wird.

## Schritte in Proxmox

1. **Backup sichern.** Ein aktuelles HA-Backup liegt ohnehin auf dem UNAS Pro.
2. **VM sauber herunterfahren** – in HA über Einstellungen → System →
   Neu starten → Ausschalten, oder auf dem Host `qm shutdown <vmid>`.
   Online-Resize funktioniert bei virtio-scsi zwar, offline ist aber
   entspannter.
3. **Vorhandene Proxmox-Snapshots löschen.** Bei qcow2 verweigert Proxmox die
   Vergrößerung, solange Snapshots existieren.
4. **Vergrößern:** VM → Hardware → Festplatte (`scsi0` bzw. `virtio0`)
   markieren → *Disk Action* → *Resize* → z. B. `+32` GiB.
   Auf der Kommandozeile: `qm resize <vmid> scsi0 +32G`.
   Nur Vergrößern ist möglich, Verkleinern nicht.
5. **VM starten.**

## Was in Home Assistant zu tun ist

**Nichts.** HAOS erledigt beides beim Booten selbst – verifiziert im Quellcode
von `home-assistant/operating-system`:

* `haos-expand.service` läuft bei jedem Systemstart vor `mnt-data.mount` und
  ruft `/usr/libexec/haos-expand` auf. Das Skript
  * verschiebt den GPT-Backup-Header ans neue Ende der Platte
    (`sfdisk --relocate gpt-bak-std`) – genau der Schritt, der nach dem
    Vergrößern nötig ist,
  * vergrößert die Partition `hassos-data` bis ans Ende (`sfdisk -N`,
    `partx -u`),
  * tut nichts, wenn weniger als ~8 MB frei sind (Ausrichtungsreste).
* `mnt-data.mount` zieht `systemd-growfs@mnt-data.service` mit
  (`Wants=`) – damit wächst das ext4-Dateisystem auf die neue
  Partitionsgröße.
* Die Unit hat `TimeoutStartSec=infinity`. Auf großen oder langsamen Platten
  kann der erste Start deshalb spürbar länger dauern; das ist kein Fehler.

**Wichtig:** Das passiert nur bei einem echten **Systemstart**. Ein
„Home Assistant neu starten" (nur Core) reicht nicht – beim Aus- und
Einschalten der VM ist das aber ohnehin gegeben.

## Kontrolle danach

Einstellungen → System → Speicher, oder in den Systeminformationen der Wert
`disk_total`. Er muss die neue Größe zeigen. Alternativ über das
Terminal-Add-on: `df -h /mnt/data`.

## Nicht nötig / nicht empfohlen

* **Zweite Platte anhängen** bringt von allein nichts. HAOS kann `/mnt/data`
  zwar auf einen anderen Datenträger verschieben (Einstellungen → System →
  Speicher → Datenträger verschieben), das ist aber eine Migration mit
  Neustart und mehr Risiko. Solange die bestehende Platte wachsen kann, ist
  das der einfachere Weg.

## Auch mit mehr Platz sinnvoll

* Aufbewahrung der automatischen Backups begrenzen: Einstellungen → System →
  Sicherungen → automatische Sicherungen.
* Recorder im Zaum halten (`purge_keep_days`), sonst wächst die SQLite-Datei
  einfach in den neuen Platz hinein.
