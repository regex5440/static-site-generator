from textnode import TextNode, TextType

def main():
    x = TextNode("This is some anchor text", TextType.LINK, "https://example.com")
    print(x)

if __name__ == "__main__":
    main()