
class HTMLNode:
    def __init__(self, tag: str | None = None, value: str | None = None, children: list['HTMLNode'] = [], props: dict = {}):
        if tag is None and len(props) > 0:
            # No tag but props provided
            raise Exception("props can only be passed with to a tag")
        if value is None and len(children) == 0:
            # No value or children provided
            raise Exception("missing value or children")

        self.tag = tag
        self.props = props
        self.value = value
        self.children = children
    
    def to_html(self):
        raise NotImplementedError()
    
    def props_to_html(self) -> str:
        if len(self.props) == 0:
            return ""
        attrs = []
        for [key, value] in self.props.items():
            attrs.append(f'{key}="{value}"')
        return ' '.join(attrs)
    
    def __repr__(self) -> str:
        # repr = "("
        # if self.tag is not None:
        #     repr += "\n" + self.tag
        # if len(self.props) > 0:
        #     repr += "\n" + self.props_to_html()

        # if self.value is not None:
        #     repr += "\n" + self.value

        # if len(self.children) > 0:
        #     repr += "\n"
        #     for child in self.children:
        #         repr += "\t-" + child.__repr__()
        # return repr

        repr = ""
        if self.tag is not None:
            repr += "<" + self.tag
        
        if len(self.props) > 0:
            repr += f' {self.props_to_html()}'

        if self.tag is not None:
            repr += ">"
        
        if self.value is not None:
            repr += self.value
        elif len(self.children) > 0:
            child = []
            for c in self.children:
                child.append(f'{c}')
            repr += "".join(child)
        
        if self.tag is not None:
            repr += f'</{self.tag}>'

        return repr
    
    def __eq__(self, value: object) -> bool:
        if type(value) == str:
            return self.__repr__() == value
        return self.__repr__() == value.__repr__()
    
class LeafNode(HTMLNode):
    def __init__(self, tag: str | None = None, value: str = "", props: dict = {}):
        if value is None:
            raise ValueError("leaf node must contain a value")
        super().__init__(tag, value,props= props)

    def to_html(self):
        return super().__repr__()
    

class ParentNode(HTMLNode):
    def __init__(self, tag: str, children: list[HTMLNode] = [], props: dict = {}):
        if tag is None or len(tag) == 0:
            raise ValueError('tag must be provided')
        if len(children) == 0:
            raise ValueError("children must be provided")
        super().__init__(tag,children=children,props= props)
    def to_html(self):
        return super().__repr__()