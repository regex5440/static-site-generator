import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode

class TestHTMLNode(unittest.TestCase):
    def test_valid(self):
        node = HTMLNode("a","a good link",props={
            "href": "https://example.com",
            "target": "_blank"
        })
        self.assertEqual(node, '<a href="https://example.com" target="_blank">a good link</a>')
    def test_tag_without_props(self):
        node = HTMLNode("p", "my text paragraph")
        self.assertEqual(node, '<p>my text paragraph</p>')

    def test_no_tag_value(self):
        node = HTMLNode(value="inner text value only")
        self.assertEqual(node, 'inner text value only')
    
    def test_tag_without_child(self):
        self.assertRaises(Exception, lambda:HTMLNode("a"))

    def test_tag_with_both_value_and_child(self):
        node = HTMLNode("a", "inner text", [HTMLNode(value="value 1")]) # only consider value
        self.assertEqual(node, "<a>inner text</a>")
    
    def test_tag_with_children(self):
        node = HTMLNode("a", children= [HTMLNode(value="value 1"), HTMLNode(tag="i",value="italic value")]) # only consider value
        self.assertEqual(node, "<a>value 1<i>italic value</i></a>")
    
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")
    
    def test_parent_html(self):
        node = ParentNode(
                "p",
                [
                    LeafNode("b", "Bold text"),
                    LeafNode(None, "Normal text"),
                    LeafNode("i", "italic text"),
                    LeafNode(None, "Normal text"),
                ],
            )
        self.assertEqual(node.to_html(), "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>")
    
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )
    

if __name__ == "__main__":
    unittest.main()