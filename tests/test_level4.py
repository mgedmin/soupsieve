"""
Test selectors level 4.

```
[foo='bar' i]
:nth-child(an+b [of S]?)
:is(s1, s2, ...) / :matches(s1, s2, ...)
:where(s1, s2, ...) allowed, but due to our environment, works like `:is()`
:not(s1, s2, ...)
:has(> s1, ...)
:any-link
:current
:past
:future
:focus-within
:focus-visible
:target-within
```

Not supported:

- `:nth-col(n)` / `:nth-last-col(n)`: This needs further understanding before implementing and would likely only be
  implemented for HTML, XHTML, and HTML5. This would not be implemented for XML.

- `E || F`: This would need more understanding before implementation. This would likely only be implemented for HTML,
  XHTML, and HTML5. This would not be implemented for XML.

- `:blank`: This applies to inputs with empty or otherwise null input.

- `:dir(ltr)`: This applies to direction of text. This direction can be inherited from parents. Due to the way Soup
  Sieve process things, it would have to scan the parents and evaluate what is inherited. it doesn't account for the CSS
  `direction` value, which is a good thing. It is doable, but not sure worth the effort. In addition, it seems there is
  reference to being able to do something like `[dir=auto]` which would select either `ltr` or `rtl`. This seems to add
  additional logic in to attribute selections which would complicate things, but still technically doable.

- `:lang(en-*)`: As mentioned in level 2 tests, in documents, `:lang()` can take into considerations information in
  `meta` and other things in the header.

- `:local-link`: In our environment, there is no document URL. This isn't currently practical.

- `:read-only` / `:read-write`: There are no plans to implement this at this time.

- `:required` / `:optional`: There are no plans to implement this at this time.

- `:placeholder-shown`: There are no plans to implement this at this time.

- `:indeterminate`: There are no plans to implement this at this time.

- `:valid` / `:invalid`: We currently to not validate values, so this doesn't make sense at this time.

- `:user-invalid`: User cannot alter things in our environment because there is no user interaction (we are not a
  browser). This will not be implemented.

- `:scope`: I'm not sure what this means or if it is even useful in our context. More information would be needed. It
  seems in an HTML document, this would normally just be `:root` as there is no way to specify a different reference at
  this time. I'm not sure it makes sense to bother implementing this.

- `:in-range` / `:out-of-range`: This applies to form elements only. You'd have to evaluate `value`, `min`, and `max`. I
  guess you can have numerical ranges and alphabetic ranges. Currently, there are no plans to implement this.

- `:default`: This is in the same vain as `:checked`. If we ever implemented that, we'd probably implement this, but
  there are no plans to do so at this time.

- `:playing` / `:paused`: Elements cannot be played or paused in our environment, so this will not be implemented.
"""
from . import util
import soupsieve as sv


class TestLevel4(util.TestCase):
    """Test level 4 selectors."""

    def test_attribute_case(self):
        """Test attribute value case insensitivity."""

        markup = """
        <div id="div">
        <p id="0" class="somewordshere">Some text <span id="1"> in a paragraph</span>.</p>
        <a id="2" href="http://google.com">Link</a>
        <span id="3" class="herewords">Direct child</span>
        <pre id="pre" class="wordshere">
        <span id="4">Child 1</span>
        <span id="5">Child 2</span>
        <span id="6">Child 3</span>
        </pre>
        </div>
        """

        self.assert_selector(
            markup,
            "[class*=WORDS]",
            [],
            flags=util.HTML5
        )

        self.assert_selector(
            markup,
            "[class*=WORDS i]",
            ["0", "3", "pre"],
            flags=util.HTML5
        )

        with self.assertRaises(SyntaxError):
            sv.compile('[id i]')

    def test_attribute_type_case(self):
        """Type is treated as case insensitive in HTML."""

        markup = """
        <html>
        <body>
        <div id="div">
        <p type="TEST" id="0">Some text <span id="1"> in a paragraph</span>.</p>
        <a type="test" id="2" href="http://google.com">Link</a>
        <span id="3">Direct child</span>
        <pre id="pre">
        <span id="4">Child 1</span>
        <span id="5">Child 2</span>
        <span id="6">Child 3</span>
        </pre>
        </div>
        </body>
        </html>
        """

        self.assert_selector(
            markup,
            '[type="test" s]',
            ['2'],
            flags=util.HTML5
        )

        self.assert_selector(
            markup,
            '[type="test" i]',
            ['0', '2'],
            flags=util.XML
        )

    def test_is_matches_where(self):
        """Test multiple selectors with "is", "matches", and "where"."""

        markup = """
        <div>
        <p>Some text <span id="1"> in a paragraph</span>.
        <a id="2" href="http://google.com">Link</a>
        </p>
        </div>
        """

        self.assert_selector(
            markup,
            ":is(span, a)",
            ["1", "2"],
            flags=util.HTML5
        )

        self.assert_selector(
            markup,
            ":is(span, a:matches(#\\32))",
            ["1", "2"],
            flags=util.HTML5
        )

        self.assert_selector(
            markup,
            ":where(span, a:matches(#\\32))",
            ["1", "2"],
            flags=util.HTML5
        )

        # Each pseudo class is evaluated separately
        # So this will not match
        self.assert_selector(
            markup,
            ":is(span):not(span)",
            [],
            flags=util.HTML5
        )

        # Each pseudo class is evaluated separately
        # So this will not match
        self.assert_selector(
            markup,
            ":is(span):is(div)",
            [],
            flags=util.HTML5
        )

        # Each pseudo class is evaluated separately
        # So this will match
        self.assert_selector(
            markup,
            ":is(a):is(#\\32)",
            ['2'],
            flags=util.HTML5
        )

    def test_multi_nested_not(self):
        """Test nested not and multiple selectors."""

        markup = """
        <div>
        <p id="0">Some text <span id="1"> in a paragraph</span>.</p>
        <a id="2" href="http://google.com">Link</a>
        <span id="3">Direct child</span>
        <pre id="pre">
        <span id="4">Child 1</span>
        <span id="5">Child 2</span>
        <span id="6">Child 3</span>
        </pre>
        </div>
        """

        self.assert_selector(
            markup,
            'div :not(p, :not([id=\\35]))',
            ['5'],
            flags=util.HTML5
        )

    def test_has(self):
        """Test has."""

        markup = """
        <div id="0" class="aaaa">
            <p id="1" class="bbbb"></p>
            <p id="2" class="cccc"></p>
            <p id="3" class="dddd"></p>
            <div id="4" class="eeee">
            <div id="5" class="ffff">
            <div id="6" class="gggg">
                <p id="7" class="hhhh"></p>
                <p id="8" class="iiii zzzz"></p>
                <p id="9" class="jjjj"></p>
                <div id="10" class="kkkk">
                    <p id="11" class="llll zzzz"></p>
                </div>
            </div>
            </div>
            </div>
        </div>
        """

        markup2 = """
        <div id="0" class="aaaa">
            <p id="1" class="bbbb"></p>
        </div>
        <div id="2" class="cccc">
            <p id="3" class="dddd"></p>
        </div>
        <div id="4" class="eeee">
            <p id="5" class="ffff"></p>
        </div>
        <div id="6" class="gggg">
            <p id="7" class="hhhh"></p>
        </div>
        <div id="8" class="iiii">
            <p id="9" class="jjjj"></p>
            <span id="10"></span>
        </div>
        """

        self.assert_selector(
            markup,
            'div:not(.aaaa):has(.kkkk > p.llll)',
            ['4', '5', '6'],
            flags=util.HTML5
        )

        self.assert_selector(
            markup,
            'div:NOT(.aaaa):HAS(.kkkk > p.llll)',
            ['4', '5', '6'],
            flags=util.HTML5
        )

        self.assert_selector(
            markup,
            'p:has(+ .dddd:has(+ div .jjjj))',
            ['2'],
            flags=util.HTML5
        )

        self.assert_selector(
            markup,
            'p:has(~ .jjjj)',
            ['7', '8'],
            flags=util.HTML5
        )

        self.assert_selector(
            markup2,
            'div:has(> .bbbb, .ffff, .jjjj)',
            ['0', '4', '8'],
            flags=util.HTML5
        )

        self.assert_selector(
            markup2,
            'div:has(> :not(.bbbb, .ffff, .jjjj))',
            ['2', '6', '8'],
            flags=util.HTML5
        )

        self.assert_selector(
            markup2,
            'div:not(:has(> .bbbb, .ffff, .jjjj))',
            ['2', '6'],
            flags=util.HTML5
        )

    def test_nth_child_of_s(self):
        """Test `nth` child with selector."""

        markup = """
        <p id="0"></p>
        <p id="1"></p>
        <span id="2" class="test"></span>
        <span id="3"></span>
        <span id="4" class="test"></span>
        <span id="5"></span>
        <span id="6" class="test"></span>
        <p id="7"></p>
        <p id="8" class="test"></p>
        <p id="9"></p>
        <p id="10" class="test"></p>
        <span id="11"></span>
        """

        self.assert_selector(
            markup,
            ":nth-child(2n + 1 of :is(p, span).test)",
            ['2', '6', '10'],
            flags=util.HTML5
        )

        self.assert_selector(
            markup,
            ":nth-child(-n+3 of p)",
            ['0', '1', '7'],
            flags=util.HTML5
        )

    def test_anylink(self):
        """Test any link (all links are unvisited)."""

        markup = """
        <div id="div">
        <p id="0">Some text <span id="1" class="foo:bar:foobar"> in a paragraph</span>.
        <a id="2" class="bar" href="http://google.com">Link</a>
        <a id="3">Placeholder text.</a>
        </p>
        </div>
        """

        self.assert_selector(
            markup,
            ":any-link",
            ["2"],
            flags=util.HTML5
        )

        self.assert_selector(
            markup,
            "a:any-link",
            [],
            flags=util.XML
        )

        self.assert_selector(
            markup,
            ":not(a:any-link)",
            ["div", "0", "1", "2", "3"],
            flags=util.XML
        )

    def test_focus_within(self):
        """Test focus within."""

        markup = """
        <form id="form">
          <input type="text">
        </form>
        """

        self.assert_selector(
            markup,
            "form:focus-within",
            [],
            flags=util.HTML5
        )

        self.assert_selector(
            markup,
            "form:not(:focus-within)",
            ["form"],
            flags=util.HTML5
        )

    def test_focus_visible(self):
        """Test focus visible."""

        markup = """
        <form id="form">
          <input type="text">
        </form>
        """

        self.assert_selector(
            markup,
            "form:focus-visible",
            [],
            flags=util.HTML5
        )

        self.assert_selector(
            markup,
            "form:not(:focus-visible)",
            ["form"],
            flags=util.HTML5
        )

    def test_target_within(self):
        """Test target within."""

        markup = """
        <a href="#head-2">Jump</a>
        <article id="article">
        <h2 id="head-1">Header 1</h1>
        <div><p>content</p></div>
        <h2 id="head-2">Header 2</h1>
        <div><p>content</p></div>
        </article>
        """

        self.assert_selector(
            markup,
            "article:target-within",
            [],
            flags=util.HTML5
        )

        self.assert_selector(
            markup,
            "article:not(:target-within)",
            ["article"],
            flags=util.HTML5
        )

    def test_current_past_future(self):
        """Test current, past, future."""

        markup = """
        <div id="div">
        <p id="0">Some text <span id="1" class="foo:bar:foobar"> in a paragraph</span>.
        <a id="2" class="bar" href="http://google.com">Link</a>
        <a id="3">Placeholder text.</a>
        </p>
        </div>
        """

        self.assert_selector(
            markup,
            ":current(p, div, a)",
            [],
            flags=util.HTML5
        )

        self.assert_selector(
            markup,
            ":current(p, :not(div), a)",
            [],
            flags=util.HTML5
        )

        self.assert_selector(
            markup,
            "body :not(:current(p, div, a))",
            ["div", "0", "1", "2", "3"],
            flags=util.HTML5
        )

        self.assert_selector(
            markup,
            "body :not(:current(p, :not(div), a))",
            ["div", "0", "1", "2", "3"],
            flags=util.HTML5
        )

        self.assert_selector(
            markup,
            "p:current",
            [],
            flags=util.HTML5
        )

        self.assert_selector(
            markup,
            "p:not(:current)",
            ["0"],
            flags=util.HTML5
        )

        self.assert_selector(
            markup,
            "p:past",
            [],
            flags=util.HTML5
        )

        self.assert_selector(
            markup,
            "p:future",
            [],
            flags=util.HTML5
        )
