import unittest

from textnode import TextNode, TextType
from helpers import text_node_to_html_node, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)
    
    def test_not_eq_url(self):
        node = TextNode("This is a text node", TextType.LINK, "https://example.com")
        node2 = TextNode("This is a text node", TextType.LINK, "https://test.org")
        self.assertNotEqual(node, node2)

    def test_invalid_usage(self):
        def callable():
            TextNode("Link type inline text", TextType.LINK)
        self.assertRaises(Exception,callable)
    
    def test_not_eq_type(self):
        node = TextNode("This is a text node", TextType.ITALIC)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_text(self):
        node = TextNode("This is a text node", TextType.REGULAR)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")
    def test_parse_md_code(self):
        node = TextNode("This is text with a `code block` word", TextType.REGULAR)
        newNodes = split_nodes_delimiter([node], "`", TextType.CODE_INLINE)
        expected = [
            TextNode("This is text with a ", TextType.REGULAR),
            TextNode("code block", TextType.CODE_INLINE),
            TextNode(" word", TextType.REGULAR),
        ]
        self.assertListEqual(newNodes, expected)
    def test_parse_md_italic(self):
        node = TextNode("_Italic text_ remains _stylish_", TextType.REGULAR)
        newNodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        expected = [
            TextNode("Italic text", TextType.ITALIC),
            TextNode(" remains ", TextType.REGULAR),
            TextNode("stylish", TextType.ITALIC),
        ]
        self.assertListEqual(newNodes, expected)
    
    def test_parse_md_bold(self):
        node = TextNode("This is **some bold text**", TextType.REGULAR)
        newNodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("This is ", TextType.REGULAR),
            TextNode("some bold text", TextType.BOLD),
        ]
        self.assertListEqual(newNodes, expected)
    def test_parse_md_bold_valid(self):
        node = TextNode("This is* some **bold text**", TextType.REGULAR)
        newNodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("This is* some ", TextType.REGULAR),
            TextNode("bold text", TextType.BOLD),
        ]
        self.assertListEqual(newNodes, expected)
            
    def test_parse_invalid_md(self):
        node = TextNode("This is `text with a `code block` word", TextType.REGULAR)
        self.assertRaises(SyntaxError, lambda:split_nodes_delimiter([node], "`", TextType.CODE_INLINE))
        node = TextNode("This is a **wrong** **bold text", TextType.REGULAR)
        self.assertRaises(SyntaxError, lambda:split_nodes_delimiter([node], "**", TextType.CODE_INLINE))
    
    def test_parse_md_image(self):
        texts = extract_markdown_images("This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)")
        expected = [("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")]

        self.assertListEqual(texts, expected)
    
    def test_parse_md_links(self):
        text = extract_markdown_links("This is text with a link [to google](https://www.google.com) and [to youtube](https://www.youtube.com/@hdxdev)")
        expected = [("to google", "https://www.google.com"), ("to youtube", "https://www.youtube.com/@hdxdev")]
        self.assertListEqual(text, expected)
    
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.REGULAR,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.REGULAR),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.REGULAR),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )
    def test_split_images_only(self):
        node = TextNode(
            "[image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.REGULAR,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("[image](https://i.imgur.com/zjjcJKZ.png) and another ", TextType.REGULAR),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )
    def test_split_link(self):
        node = TextNode(
            "[link text](https://i.imgur.com/zjjcJKZ.png) and another [second link](https://i.imgur.com/3elNhQu.png)",
            TextType.REGULAR,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("link text", TextType.LINK, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.REGULAR),
                TextNode(
                    "second link", TextType.LINK, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )
    def test_md_text_conversion(self):
        nodes = text_to_textnodes("This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://hdxdev.in)")
        expected = [
            TextNode("This is ", TextType.REGULAR),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.REGULAR),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.REGULAR),
            TextNode("code block", TextType.CODE_INLINE),
            TextNode(" and an ", TextType.REGULAR),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.REGULAR),
            TextNode("link", TextType.LINK, "https://hdxdev.in"),
        ]
        self.assertListEqual(nodes, expected)

if __name__ == "__main__":
    unittest.main()