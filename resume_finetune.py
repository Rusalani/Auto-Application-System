from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.edmundson import EdmundsonSummarizer
import nltk
from jinja2 import Environment, FileSystemLoader
from nltk.corpus import stopwords
import re
import json
import spacy
import os

SIGNIFICANT_WORDS = {'degree', 'tools', 'frameworks', 'company', 'knowledge',
                     'years', 'experience', 'proficient', 'seeking', 'background', 'build',
                     'advantage', 'prior'}
STIGMA_WORDS = {'staffing', 'benefits', 'travel', 'located', 'submit', 'pay', 'discriminate',
                'employer', 'collaborate', 'ability', 'sponsorship', 'diversity',
                'subcontracted', 'reimbursed', 'perks', 'join', 'fulltime', 'contract', 'w2',
                'title'}
WORDS_TO_REMOVE = {'about the job', 'company description', 'role summary', 'role description',
                   'compensation and benefits', '', 'key responsibilities',
                   'educational/experience requirements', 'position summary', 'position duties',
                   'position skills', 'ideal candidate',
                   'preferred qualifications', 'areas of responsibility', 'job description',
                   'certifications & licenses', 'experience and education',
                   'our company'}
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
          'October', 'November', 'December']
# en_core_web_lg
NLP = spacy.load('en_core_web_lg')

try:
    STOP_WORDS = stopwords.words('english')
except LookupError:
    nltk.download('stopwords')
    STOP_WORDS = stopwords.words('english')


def summarize_job(s: str, min_sentences: int = 7) -> str:
    def remove_banned(s: str, words: [list, set]) -> str:
        pattern = '|'.join(words)
        return re.sub(pattern, '', s, flags=re.I)

    s = remove_banned(s, WORDS_TO_REMOVE)
    s = list(filter(lambda l: l.count(' ') > 1, s.split('\n')))
    sentences_count = max(min_sentences, int(len(s) / min_sentences))

    def strip_non_ascii(string: str) -> str:
        t = ''.join((c for c in string if 0 < ord(c) < 127)).strip()
        if len(t) == 0:
            return ''
        elif t[-1] != '.':
            t += '.'
        return t

    s = ' '.join(list(map(strip_non_ascii, s))).strip()
    summarizer = EdmundsonSummarizer()
    summarizer.null_words = STOP_WORDS
    summarizer.bonus_words = SIGNIFICANT_WORDS
    summarizer.stigma_words = STIGMA_WORDS
    parser = PlaintextParser.from_string(s, Tokenizer("english"))
    summary = summarizer(parser.document, sentences_count)
    t = ' '.join([str(sentence) for sentence in summary])
    return t


def findsim(text: str, data: list[str]) -> tuple[list[str], float]:
    base = NLP(text)
    queue = []
    for x in data:
        test = NLP(x)
        sim = base.similarity(test)
        queue.append((sim, x))
    queue = list(zip(*sorted(queue, reverse=True)))
    return list(queue[1]), sum(queue[0])


def load_experience(t, job_num: int = 4, job_duties: int = 3, proj_duties: int = 2,
                    proj_num: int = 2):
    BLANKSPACEINRESUME = 22
    worklength = []
    projlength = []

    def factors(x):
        l = []
        for i in range(1, x + 1):
            if x % i == 0:
                l.append([i, x // i])
        return l

    def select_duies(info, length, max_len, proj=False):

        if proj:
            length = length[:2]

        bullet_points = max_len // len(length)
        filler = max_len % len(length)

        for x in range(len(length)):
            if length[x] - bullet_points < 0:
                filler += bullet_points - length[x]
            else:
                length[x] = bullet_points
        length[0] += filler
        for x in range(len(length)):
            info[x]['duties'] = info[x]['duties'][:length[x]]

        return info[:len(length)]

    with open('user_info\\start up.json', 'r') as file:
        info = json.load(file)

    for x in range(len(info['work experience'])):
        response = findsim(t, info['work experience'][x]['duties'])[0]
        response = [x.replace('%', '\%') for x in response]
        info['work experience'][x]['duties'] = response
        worklength.append(len(response))

    if len(info['project experience']) > 0:
        queue = []
        for x in range(len(info['project experience'])):
            response, score = findsim(t, info['project experience'][x]['duties'])
            queue.append((score, x))
            response = [x.replace('%', '\%') for x in response]
            info['project experience'][x]['duties'] = response
            projlength.append(len(response))
        info['project experience'] = [info['project experience'][i] for i in
                                      list(zip(*sorted(queue, reverse=True)))[1]]

        info['work experience'] = select_duies(info['work experience'], worklength,
                                               int(3 * BLANKSPACEINRESUME / 4))
        info['project experience'] = select_duies(info['project experience'], projlength,
                                                  int(BLANKSPACEINRESUME / 4), True)
    else:
        info['work experience'] = select_duies(info['work experience'], worklength,
                                               BLANKSPACEINRESUME)

    return info


def date_change(deets):
    for x in deets['work experience']:
        date_change2(x)
    for x in deets['education']:
        date_change2(x)
    for x in deets['project experience']:
        date_change2(x)
    return deets


def date_change2(x):
    parts = x['start'].split('/')
    x['start'] = MONTHS[int(parts[0]) - 1] + ' ' + parts[1]
    parts = x['end'].split('/')
    x['end'] = MONTHS[int(parts[0]) - 1] + ' ' + parts[1]


def write_resume(job_description: str, title: str = None, company: str = None,
                 location: str = None):
    env = Environment(loader=FileSystemLoader(""),
                      variable_start_string='<<',
                      variable_end_string='>>',
                      comment_start_string='<#',
                      comment_end_string='#>',
                      block_start_string='<%',
                      block_end_string='%>')

    template = env.get_template('cv_12.tex')

    userinfo = load_userinfo()
    deets = load_experience(job_description)
    deets = date_change(deets)
    if location is not None and 'remote' in location:
        location = None
    content = template.render(email=userinfo['email'], first_name=userinfo['first name'],
                              last_name=userinfo['last name'],
                              phone_number=userinfo['number'], my_job=deets['work experience'],
                              my_project=deets['project experience'],
                              my_edu=deets['education'],
                              linkedin=userinfo['linkedin'], github=userinfo['github'],
                              location=location)
    with open('Resume.tex', 'w') as m:
        m.write(content)

    def helper(l):
        dic = {}
        for x in l:
            dic[x['job title']] = []
            for y in x['duties']:
                dic[x['job title']].append(y)
        return dic

    work = helper(deets['work experience'])
    proj = helper(deets['project experience'])
    os.system("xelatex Resume.tex -quiet")
    return work, proj


def load_userinfo():
    with open('user_info\\responses.json', 'r') as file:
        info = json.load(file)
    if 'linkedin' in info and 'www.' in info['linkedin']:
        info['linkedin'] = info['linkedin'].split('www.', 1)[1].capitalize()
    if 'github' in info and 'www.' in info['github']:
        info['github'] = info['github'].split('www.', 1)[1].capitalize()
    info['email'] = info['email'].capitalize()
    info['number'] = '(' + info['number'][:3] + ')-' + info['number'][3:6] + '-' + info['number'][
                                                                                   6:]
    return info


if __name__ == "__main__":
    with open("testjob.txt", "r") as f:
        text = f.read()
    job = summarize_job(text)
    print(job)
    work, proj = write_resume(job)


    def print_exp(l):
        for x in l:
            print(x)
            for y in l[x]:
                print('-' + y)


    print_exp(work)
    print_exp(proj)
