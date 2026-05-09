# Changelog

All notable changes to this project will be documented in this file.

## [1.1.9] - 2026-05-09

- Fixed E2E tests: Unit Converter input type validation
- Fixed E2E tests: QR Generator canvas visibility checks
- Fixed Accessibility tests: Corrected path to tool configuration
- Timezone Calculator: Added European date format support (DD.MM.YYYY)
- Time Converter: Enhanced date parsing for multiple formats

## [1.1.8] - 2026-05-09

- New tool: Timezone Calculator with automatic DST handling and searchable timezones
- New tool: Website Source Code Viewer
- New tool: Redirect Follower
- New tool: Cozy Fireplace with CSS animations
- QR Generator: Fixed SVG export
- Money Counter: Added 12 more currencies (15 total)
- Stats: Enhanced bot detection, country/referrer tracking, bandwidth tracking
- Security: Added security.txt with dynamic expiration

## [1.1.7] - 2026-01-27

- Enhanced textarea: configurable controls panel with syntax highlighting, text transforms, and undo/redo history
- URL Checker: identifies itself in User-Agent, respects robots.txt (uses HEAD request when disallowed)
- New tool: Resistor Color Code Calculator (3-6 band resistors with IEC 60062 standard)
- New tool: Ohm's Law Calculator (voltage, current, resistance, power)
- New tool: IPv4 Subnet Calculator (network address, broadcast, host range, subnets list)
- New tool: IPv6 Subnet Calculator (prefix calculation, address expansion/compression)
- New tool: Money Counter (count bills and coins in EUR, USD, GBP)

## [1.1.6] - 2026-01-24

- Clean up old accessibility reports (only keep latest version)
- Update workflow to auto-delete old reports before adding new

## [1.1.5] - 2026-01-24

- Fix `.bg-success` contrast in high-contrast mode (AAA compliance)
- Fix support toast contrast in dark and high-contrast modes
- Fix heading order: tile titles now use `<span>` instead of `<h5>`
- Add accessibility badge to README
- Split accessibility tests into separate jobs per theme
- Add URL checker and DNS lookup with params to accessibility tests

## [1.1.0] - 2026-01-24

- **Dark mode**: Toggle between light and dark themes, respects your system preference
- New tool: BMI Calculator with visual BMI scale
- New tool: Stopwatch with lap times
- New tool: URL Checker - check redirects, SSL, and content changes
- New tool: Time Converter between timezones
- New tool: Map Maker - place markers and export coordinates
- Improved accessibility with better color contrast
- Automated accessibility testing for all tools

## [1.0.22] - 2026-01-15

- New tool: Dice roller with coin flip mode
- Custom dice support (any number of sides ≥ 3)
- Share button improvements for DNS lookup, colorblind simulator, radius, and distance tools
- URL state management for shareable links

## [1.0.21] - 2026-01-15

- Add share button to all tools
- Unit converter: German translations, proper superscripts (km², cm²), local convert library
- Ko-fi toast positioning and duration fixes

## [1.0.20] - 2026-01-15

- Starting point for changelog
