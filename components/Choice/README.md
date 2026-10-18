Pick-one options shown as buttons: each has a radio circle; the chosen one is `action-tint` with an `action` ring and a bold label, and its circle holds an `action` dot (D26). Ticks are for multi-select only.

Use it instead of radio dots for any short choice (format, seal, window type, where the unit is). It is a native radio group underneath: wrap the options in `.ws-choice` with `role="radiogroup"` and an `aria-label`, one `label.ws-choice__opt` per option holding an `input.ws-choice__input` (visually hidden) and a `span.ws-choice__face` with the text. The chosen face is ringed and bold and its radio dotted, so the state never relies on colour; the arrow keys move between options. Keep labels to one or two words and a run to about four or five options; more than that becomes a `Gallery`, or runs under captions. Always have one chosen by default; the one exception is the view choice over the 3D stage, which shows the side the camera faces and clears when the user turns away (Workbench, D30). When one choice comes in groups (Skådis Air's "Boards" and "Connectors"), caption each run with a `.ws-caps` line; a caption straight after a run of buttons keeps a gap above it.

When the groups are long, switch between them instead (D57): a Choice of the groups ("Boards | Connectors") above one Choice per group, each a radio group of its own named for its group, and every list but the chosen group's given the `hidden` attribute. The stylesheet makes `hidden` hide anything it styles, whatever display a class sets (the browser's own rule loses to a Choice's, so a hidden Choice stayed on show), and `check-previews.py` fails if anything is still drawn with it. Each list keeps its own chosen option while hidden, so switching back shows the type last chosen in that group; a tool that remembers the choices across visits stores each group's type beside the group (Skådis Air keeps them in this browser).

```html
<div class="ws-choice" role="radiogroup" aria-label="Boards or connectors">
  <label class="ws-choice__opt"><input class="ws-choice__input" type="radio" name="group" value="boards" checked><span class="ws-choice__face">Boards</span></label>
  <label class="ws-choice__opt"><input class="ws-choice__input" type="radio" name="group" value="connectors"><span class="ws-choice__face">Connectors</span></label>
</div>
<div class="ws-choice" role="radiogroup" aria-label="Board" data-group="boards">
  <label class="ws-choice__opt"><input class="ws-choice__input" type="radio" name="board" value="solid" checked><span class="ws-choice__face">Solid</span></label>
  <label class="ws-choice__opt"><input class="ws-choice__input" type="radio" name="board" value="skeleton"><span class="ws-choice__face">Skeleton</span></label>
</div>
<div class="ws-choice" role="radiogroup" aria-label="Connector" data-group="connectors" hidden>
  <label class="ws-choice__opt"><input class="ws-choice__input" type="radio" name="connector" value="clip" checked><span class="ws-choice__face">Slot clip</span></label>
  <label class="ws-choice__opt"><input class="ws-choice__input" type="radio" name="connector" value="hook"><span class="ws-choice__face">Hook</span></label>
</div>
```

In the tool's script, show the chosen group's list and hide the others; the type is the chosen option of the list on show:

```js
const lists = document.querySelectorAll('.ws-choice[data-group]');
for (const pick of document.querySelectorAll('input[name="group"]'))
  pick.addEventListener('change', () => {
    for (const list of lists) list.hidden = list.dataset.group !== pick.value;
  });
const type = () => document.querySelector('.ws-choice[data-group]:not([hidden]) :checked').value;
```
