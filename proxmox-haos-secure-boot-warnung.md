# Proxmox-Warnung beim Start der HA-VM: "EFI disk without 'ms-cert=2023k'"

Stand: 2026-09-02. Betrifft **VM 102** (Home Assistant OS 18.2, `board: ova`)
auf dem Node `pve`. Die Meldung erscheint im Task-Log bei *jedem* VM-Start.

## Die Meldung

```
WARN: EFI disk without 'ms-cert=2023k' option, suggesting that not all UEFI 2023
certificates from Microsoft are enrolled yet.
The UEFI 2011 certificates expire in June 2026! ...
Use 'Disk Action > Enroll Updated Certificates' in the UI or, while the VM is
shut down, run 'qm enroll-efi-keys 102' to enroll the new certificates.
```

## Einordnung: für diese VM ist sie folgenlos

Es geht um **Secure Boot**. Microsofts UEFI-Zertifikate von 2011 laufen im Juni
2026 ab; Bootloader, die mit den 2023er Zertifikaten signiert sind, werden von
einer EFI-Disk mit nur den alten Zertifikaten abgewiesen. Das trifft Windows
und die großen Linux-Distributionen.

**Home Assistant OS gehört nicht dazu.** Nachgesehen im Quellcode von
`home-assistant/operating-system`:

* `buildroot-external/board/pc/ova/meta` setzt `BOOTLOADER=grub`, und
  `configs/ova_defconfig` baut GRUB2 selbst (`BR2_TARGET_GRUB2_X86_64_EFI=y`).
* `board/pc/ova/haos-hook.sh` legt den Bootloader unter `EFI/BOOT/` ab, also
  im Fallback-Pfad `\EFI\BOOT\BOOTX64.EFI`.
* Im gesamten Repository gibt es für x86 **keinen Shim, keine SBAT-Metadaten
  und keine Signatur** – die einzigen Secure-Boot-Treffer betreffen
  ARM-Boards (Hardkernel, Khadas).

Der GRUB von HAOS ist damit **unsigniert**. Mit aktivem Secure Boot würde die
VM überhaupt nicht starten. Da sie startet, ist Secure Boot in dieser VM
abgeschaltet, und die hinterlegten Microsoft-Zertifikate werden schlicht nicht
benutzt. Im Juni 2026 passiert hier nichts.

## Warum die Warnung trotzdem kommt

Proxmox prüft nur das Konfigurations-Flag, nicht den tatsächlichen Zustand.
In `PVE/QemuServer/OVMF.pm`:

```perl
sub should_enroll_ms_2023_cert {
    my ($efidisk) = @_;
    return if !$efidisk->{'pre-enrolled-keys'};
    return if $efidisk->{'ms-cert'} && $efidisk->{'ms-cert'} eq '2023k';
    return 1;
}
```

`check_efi_vars()` in `PVE/QemuServer.pm` gibt die Warnung bei jedem Start aus,
sobald diese Funktion wahr liefert. Die VM wurde also mit *Pre-Enrolled Keys*
angelegt (Proxmox-Standard bei OVMF) – mehr sagt die Meldung nicht aus.

Der Absatz zu **BitLocker** ist reine Windows-Information und hier
gegenstandslos.

## Zwei Möglichkeiten

**A – Ignorieren.** Funktional korrekt. Nachteil: Die Warnung steht bei jedem
Start im Task-Log und verdeckt dort irgendwann echte Meldungen.

**B – Zertifikate nachziehen (empfohlen, ~10 Sekunden).**

1. VM 102 herunterfahren (der Befehl verlangt eine gestoppte VM).
2. Entweder in der GUI: VM 102 → Hardware → EFI Disk → *Disk Action* →
   *Enroll Updated Certificates*.
   Oder auf dem Host: `qm enroll-efi-keys 102`
3. VM starten. In der Konfiguration steht danach `efidisk0: …,ms-cert=2023k`,
   die Warnung bleibt weg.

Angefasst wird dabei nur die wenige hundert KB große EFI-Variablen-Disk, nicht
die Datenplatte. Für HAOS ist der Vorgang folgenlos, weil Secure Boot ohnehin
nicht genutzt wird – er räumt lediglich die Meldung weg.

## Nicht anfassen

`pre-enrolled-keys` nachträglich auf 0 stellen bringt nichts und erfordert ein
Neuanlegen der EFI-Disk. Kein Gewinn gegenüber Variante B.

## Andere VMs

Die Warnung gilt pro VM. Bei **Windows-VMs mit aktivem Secure Boot** ist das
Nachziehen vor Juni 2026 wirklich nötig – und dort gilt der BitLocker-Hinweis:
vor dem Enrollment je Laufwerk `manage-bde -protectors -disable <drive>`
ausführen, sonst wird beim nächsten Start der Wiederherstellungsschlüssel
verlangt.
