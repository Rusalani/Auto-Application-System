%----------------------------------------------------------------------------------------
%	CLASS OPTIONS AND REQUIRED PACKAGES
%----------------------------------------------------------------------------------------

\ProvidesClass{deedy-resume}[2014/04/30 CV class]
\NeedsTeXFormat{LaTeX2e}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass{article}

\usepackage[hmargin=0.75cm, vmargin=0.5cm]{geometry} % Specifies horizontal and vertical page margins
%----------------------------------------------------------------------------------------
%       DISABLE ALL ERROR MESSAGES
%----------------------------------------------------------------------------------------
\usepackage{silence}
%\WarningsOff*

%----------------------------------------------------------------------------------------
%	COLORS
%----------------------------------------------------------------------------------------

\usepackage[usenames,dvipsnames]{xcolor} % Required for custom colors

\definecolor{primary}{HTML}{2b2b2b} % The primary document color for content text
\definecolor{headings}{HTML}{9554c8} % The color of the large sections
\definecolor{subheadings}{HTML}{f9bc2f} % The color of subsections and places worked/studied
\definecolor{subheadings2}{HTML}{cd5c5c}

%----------------------------------------------------------------------------------------
%	FONTS
%----------------------------------------------------------------------------------------

\usepackage{fontspec} % Required for specifying custom fonts in XeLaTeX
\defaultfontfeatures{Mapping=tex-text,Scale=MatchLowercase}
\setmainfont[Path = fonts/lato/]{Lato-Lig}
%----------------------------------------------------------------------------------------
%	MAIN HEADING COMMAND
%----------------------------------------------------------------------------------------

\newcommand{\namesection}[3]{ % Defines the command for the main heading
\centering{ % Center the name
\fontsize{25pt}{50pt} % Font size
\fontspec[Path = fonts/lato/]{Lato-Lig}
\selectfont #1 % First name font
\fontspec[Path = fonts/lato/]{Lato-Lig}
\selectfont #2 % Last name font
} \\[1pt] % Whitespace between the name and contact information
\centering{ % Center the contact information
\color{subheadings} % Use the headings color
\fontspec[Path = fonts/lato/]{Lato-Lig}\fontsize{10pt}{14pt}
\selectfont #3} % Contact information font
\noindent\makebox[\linewidth]{\color{headings}\rule{\paperwidth}{0.6pt}} % Horizontal rule
%\vspace{-10pt} % Reduce whitespace after the rule slightly

}

%----------------------------------------------------------------------------------------
%	SECTION TITLE STYLING AND SPACING
%----------------------------------------------------------------------------------------

\usepackage{titlesec} % Required for customizing section/subsection/etc titles

\titlespacing{\section}{0pt}{0pt}{0pt} % Removes the spacing around the main section titles
\titlespacing{\subsection}{0pt}{0pt}{0pt} % Removes the spacing around the subsections
\newcommand{\sectionspace}{\vspace{4pt}} % Defines a command to add a set amount of space after sections and subsections


\titleformat{\section}{ % Customize the large section titles
\color{headings}\scshape\fontspec[Path = fonts/lato/]{Lato-Bol}\fontsize{14pt}{22pt}\selectfont \raggedright\uppercase}{}{}{}

\titleformat{\subsection}{ % Customize the subsections and places worked/studied titles
\color{subheadings}\fontspec[Path = fonts/lato/]{Lato-Bol}\fontsize{11pt}{14pt}\selectfont\bfseries}{}{}{}

\newcommand{\runsubsection}[1]{ % Used for creating subsections where a description is required on the same line
\color{subheadings}\fontspec[Path = fonts/lato/]{Lato-Bol}\fontsize{11pt}{14pt}\selectfont\bfseries {#1} \normalfont}

\newcommand{\descript}[1]{ % Used for describing the subsection either on the same line or underneath
\color{primary}\raggedright\scshape\fontspec[Path = fonts/lato/]{Lato-Bol}\fontsize{10pt}{12pt}\selectfont {#1 \\} \normalfont}

\newcommand{\location}[1]{ % Used for specifying a duration and/or location under a subsection
\color{primary}\raggedright\fontspec[Path = fonts/lato/]{Lato-Bol}\fontsize{10pt}{12pt}\selectfont {#1\\} \normalfont}

\newcommand{\ljobname}[1]{ % Used for specifying a duration and/or location under a subsection
\color{subheadings2}\raggedright\fontspec[Path = fonts/lato/]{Lato-Bol}\fontsize{10pt}{12pt}\selectfont {#1\\} \normalfont}

%----------------------------------------------------------------------------------------
%	SECTION TITLE STYLING AND SPACING
%----------------------------------------------------------------------------------------

\newenvironment{tightitemize} % Defines the tightitemize environment which modifies the itemize environment to be more compact
{\vspace{-\topsep}\begin{itemize}\itemsep1pt \parskip0pt \parsep0pt}
{\end{itemize}\vspace{-\topsep}}