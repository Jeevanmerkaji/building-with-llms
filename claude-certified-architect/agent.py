import anthropic
import json
import os

#----------------------
# Step 2
# Read the anthropic api key
# Never hardcode the key here
#-------------------

client =  anthropic.Anthropic()

#----------------------
#Step 3
# each field will have 3 required fields
# name - what claude calls it in the tool_use blocks
# desciption -  how claude decides when to use this tool
# inpt_schema-  JSON schema defining the tools parameters
#0--------------------------------

tools =  [
    {
        "name" :  "lookuo_order",
        "description" : (
            "Look up the order by its order_id"
            "Returns current status, estimated deliver date and carrier name"
            "Use this when the customer asks where thier order is or when it is arrived"

        ),
        "input_schema": {
            "type" : "object",
            "properties": {
                "order_id" :{
                    "type": "string",
                    "description" : "The numeric order ID (eg. '4821')"


                }
            },
            "required" : ["order_id"]
        } 
    }

]


#--------------------------
# Implementing the tool functions 
# Step 4
# cladue cannot call these functions directly
# Claude REQUESTS a tool call -> your code runs it -> you retunr the results 
# This is the mock implementation because in the production it will query the database.

def execute_tool(tool_name :str, tool_input:dict ) -> str:
    """Run a tool and return its result as a JSON string"""
    if tool_name == "lookup_order":
        order_id =  tool_input.get("order_id" , " ")
        mock_orders = {
            "4821": {"status": "shipped",    "eta": "March 30", "carrier": "FedEx"},
            "9910": {"status": "processing", "eta": "April 2",  "carrier": "UPS"},
            "0042": {"status": "delivered",  "eta": "March 25", "carrier": "DHL"},
        }

        if order_id in mock_orders:
            return json.dumps(mock_orders[order_id])

        else:
            return json.dumps({"error" : f"order {order_id} not found"})


    return json.dumps({"error": f"Unknown tool : {tool_name}"})

def handle_tool_call(tool_name : str , tool_id :  str, tool_input :dict) -> dict :
    """
        Execute the tool call and return a complete tool_result dict.
        Structured error categories let claude decide : retry, self_correct or escalate
        transient -> infrastructure hicup ; retryable after a delay
        permission -> access denied , esclate, dont retry
        validation -> bad params; model should self-correct before retrying
        internal -> unexpected; surface to coordinator / human

    
    """

    print(f"  Calling tool: {tool_name}({tool_input})")

    try:
        content = execute_tool(tool_name , tool_input)
        print(f"  Result: {content}")
        return {
            "type" : "tool_result",
            "tool_use_id" : tool_id,
            "content" : content
        }

    except TimeoutError as e:
        # Transient -  infrastructure hicup :  its like safe to retry after a delay
        print (f" ERROR:  TimeoutError on {tool_name}")

        return {
            "type" :  "tool_result" ,
            "tool_use_id" :  tool_id,
            "is_error" : True,
            "content" : json.dumps({
                "errorCategory" : "transient",
                "isRetryable" : True,
                "desctiption" : f"Timeout calling {tool_name} : {str(e)}",
                "retryAfterMS" :  2000
            })
        }

    except PermissionError as e:
        # permission -> agent lacks the access;  retrying wont help, escalate
        print (f" ERROR: PermissionError on {tool_name}")

        return {
            "type" : "tool_result",
            "tool_use_id" : tool_id,
            "is_error" : True,
            "content":json.dumps( {
                "errorCategory" : "permission",
                "isRetryable" : False,
                "description" : f"Access  denied for {tool_name} : {str(e)}",
            } ),
        }
    
    except ValueError  as e:
        # ❌ Validation — bad input params; model should self-correct, not retry
        print(f"  ← ERROR: ValueError on {tool_name}")
        return {
            "type":        "tool_result",
            "tool_use_id": tool_id,
            "is_error":    True,
            "content":     json.dumps({
                "errorCategory": "validation",
                "isRetryable":   False,
                "description":   f"Invalid input for {tool_name}: {str(e)}",
            }),
        }
    except Exception as e:
        # 💥 Internal — unexpected; log and surface to coordinator
        print(f"  ← ERROR: {type(e).__name__} on {tool_name}")
        return {
            "type":        "tool_result",
            "tool_use_id": tool_id,
            "is_error":    True,
            "content":     json.dumps({
                "errorCategory": "internal",
                "isRetryable":   False,
                "description":   f"Unexpected error in {tool_name}: {str(e)}",
            }),
        }



# Step 5 :The agentic loop
#-----------------------------

def  run_agent(user_message: str) -> str:
    """
        Run the agentic loop until claude produces a final answer
        Returns the final text response
    """

    # Start with just the users message
    # The message array will grow on every loop iteration\

    messages = [
        {
            "role" : "user",
            "content" :  user_message
        }
    ]

    MAX_ITERATIONS = 50 
    iteraion = 0

    while iteraion < MAX_ITERATIONS:
        iteraion += 1

        ## Do the API CALL
        # Send the current message  +  the available tools to the Claude.
        # Claude returns a response with a stop_reason
        # --------------------

        response = client.messages.create(
            model = "claude-haiku-4.5" ,
            max_tokens =  4000,
            tools =  tools,
            messages =  messages
        )

        #---EXIT Condition------
        # when the stop_reason == "end_turn" means the claude is done.
        # Extract the text and return it to the caller.
        # This is the ONLY valid primary loop exit.

        if response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    return block.text
            return "" # end turn with no text (rare but possible)



        ## -----Tool use -----
        # When the stop_reason == tool_use means claude wants to call the tools.
        # We must : execute the tools, then append both messages to the history.

        if response.stop_reason == "tool_use":

            # Append the assistants message (role: "assistant")
            # This saves claudes tool requests into the conversation history.
            # You must append this before the tool_results.

            messages.append({
                "role" : "assistant",
                "content" : response.content
            })

            ## Execute the each tool_call - handle_tool_call owns all the error handling

            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    tool_results.append(handle_tool_call(block.name, block.id, block.input))

            # Append 2 :  The tool results  (role: "user")
            # "user"  role because this is data coming into the claude from the code.
            #$ Even though no humans typed this, it uses the user role

            messages.append({
                "role" : "user" , 
                "content" : tool_results
            })

            ## Loop continues - goes back to the top if the while loop
            # claude will now see the tool results and decide what to do next.

    return "ERROR : agent did not complete within the iteration limit"



# step 6 runit

if __name__ == "__main__":
    print("Running agent.....")
    answer = run_agent("Where is my order #4821?")
    print (f" Final Answer : {answer}")


    