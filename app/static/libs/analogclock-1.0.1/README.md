# Simple Analog Clock

An east-to-use analog clock widget for web pages.

## Features

* Vecter images to fit any size
* Not affected by user's time zone
* No external resources/dependencies

## How to use

1. Load `clock.min.js` in your html file.
2. Add `<div id="clock">` where you want to place it.

The analog clock will then be sized to match the width of the parent element.

## Example

```html
<div style="width: 20%; margin: auto;">
    <div id="clock" offset="+09:00" second="false"></div>
</div>

<script src="clock.min.js"></script>
```

## Options

* `offset`: "+HH\:MM" or "-HH\:MM" to specify a time offset from UTC.
* `second`: "true" or "false" to use or not use the second hand.

## Notes

This widget does not support daylight saving time.
