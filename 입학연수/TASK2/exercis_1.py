import json
import os
import random

state_file = "state.json"

DEFAULT_QUIZZES = [
    {"question": "대한민국의 수도는 어디입니나까 ? ","answer":"서울","options":["서울","부산","대전","제주"]},
    {"question": "다음중 동물이 아닌것은 ?","answer":"지렁이","options":["지렁이","사자","개","고양이"]},
]

class Quiz:
    def __init__(self,question:str,answer:str,options:list[str]):
        self.question = question
        self.answer   = answer
        self.options  = options
        
    def to_dict(self) -> dict:
        return{
            "question": self.question,
            "answer" : self.answer,
            "options": self.options
        }
    @classmethod    
    def from_dict(cls, data:dict)-> "Quiz":
        return cls(
            question = data["question"],
            answer   = data["answer"],
            options  = data["options"],
        )
    def display(self,index:int) -> None:
        print(f"\n[문제 {index}] {self.question}")
        shuffled = self.options[:]
        random.shuffle(shuffled)
        for i,opt in enumerate(shuffled,1):
            print(f" {i}. {opt}")
        self._shuffled_options = shuffled
    def check_answer(self,user_input:str) -> bool:
        try:
            choice = int(user_input)
            if 1 <= choice <= len(self._shuffled_options):
                return self._shuffled_options[choice - 1]== self.answer
        except (ValueError, AttributeError):
            pass
        return False
        
        
class QuizGame:
    def __init__(self):
        self.quizzes: list[Quiz]=[]
        self.high_score: int = 0
        self._load_state()
      
    def _load_state(self) -> None:
        if os.path.exists(state_file):
            try:
                with open(state_file,"r",encoding="utf-8") as f:
                    data = json.load(f)
                self.quizzes = [Quiz.from_dict(q) for q in data.get("quizzes",[])]
                self.high_score = data.get("high_score",0)
            except (json.JSONDecodeError,KeyError):
                print("저장 파일을 불러오는 중 오류가 발생 했습니다. 기본 데이터를 사용합니다.") 
        else:
            self.quizzes = [Quiz.from_dict(q) for q in DEFAULT_QUIZZES]
            self.high_score = 0
            self._save_state()
        
    def _save_state(self) -> None:
        data = {
            "quizzes": [q.to_dict() for q in self.quizzes],
            "high_score": self.high_score,
        }
        with open(state_file,"w",encoding="utf-8") as f:
            json.dump(data,f,ensure_ascii=False,indent=2)
            
    def _add_quiz(self) -> None:
        print("\n[새 퀴주 추가]")
        question = input("질문을 입력하세요").strip()
        if not question:
            print("질문이 비어 있습니다.")
            return 
        answer = input("정답을 입력하세요").strip()
        if not answer:
            print("정답이 비어 있습니다")
            return
        options = [answer]
        print(f"오답 3개를 입력하세요")
        for k in range(1,4):
            while True:
                wrong = input(f"   오답 {k} : ").strip()
                if wrong and wrong not in options:
                    options.append(wrong)
                    break
                print("비어 있거나 중복된 값입니다. 다시 입력해 주세요.")
        
        new_quiz = Quiz(question=question,answer=answer,options=options)
        self.quizzes.append(new_quiz)
        self._save_state()
        print(f"퀴즈가 추가되었습니다. (현재 총 {len(self.quizzes)}개)")
        
    def _show_quiz_list(self) -> None:
        if not self.quizzes:
            print("\n등록된 퀴즈가 없습니다.")
            return
        print(f"\n[퀴즈 목록 - 총 {len(self.quizzes)}]")
        print("-" * 50)
        for i,quiz in enumerate(self.quizzes,1):
            print(f" {i:2}. {quiz.question}")
            print(f"      정답: {quiz.answer}")
        print("-" * 50)
        
    def _show_high_score(self) -> None:
        print(f"\n 현재 최고 점수: {self.high_score}")
        
        
            
    # 메뉴
    def run(self) -> None:
        print("\n" + "=" * 45)
        print(" 퀴즈 Game ")
        print("=" * 45)
        while True:
            self._print_menu()
            choice = input(" 선택 : ").strip()
            if choice == "1":
                self._play_quiz()
            elif choice == "2":
                self._add_quiz()
            elif choice == "3":
                self._show_quiz_list()
            elif choice == "4":
                self._show_high_score()
            elif choice == "5":
                print("\n게임을 종료료 합니다 \n")
                break
            else:
                print("올바른 번호를 입력해 주세요 (1~5).")
                
    def _print_menu(self) -> None:     
        print("\n" + "-" * 35)
        print("  1. 퀴즈 풀기")
        print("  2. 퀴즈 추가")
        print("  3. 퀴즈 목록")
        print("  4. 최고 점수 확인")
        print("  5. 종료")
    
    def _play_quiz(self) -> None:
        if not self.quizzes:
            print("\n등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return
        
        count_input = input(f"\n 몇 문제를 풀까요 ? (1~{len(self.quizzes)})").strip()
        if count_input == "":
            pool = self.quizzes[:]
        else:
            try:
                count = int(count_input)
                if not (1 <= count <= len(self.quizzes)):
                    raise ValueError
                pool = random.sample(self.quizzes,count)
            except ValueError:
                print("유효 하지 않은 입력입니다. 전체 문제로 진행합니다.")
                pool = self.quizzes[:]
                
        random.shuffle(pool)
        score = 0
        
        for i,quiz in enumerate(pool,1):
            quiz.display(i)
            answer = input("  답 입력 (번호): ").strip()
            if quiz.check_answer(answer):
                print("정답")
                score += 1
            else:
                print(f"오답! 정답은 [{quiz.answer}] 입니다.")  
                              
    
if __name__=="__main__":
    game = QuizGame()
    game.run()
    
    